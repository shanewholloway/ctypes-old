# requires ctypes 0.9.3 or later
import new

try:
    set
except NameError:
    from sets import Set as set

from ctypes import *
from comtypes.GUID import GUID
_GUID = GUID
IID = GUID
DWORD = c_ulong

################################################################
CLSCTX_INPROC_SERVER = 1
CLSCTX_INPROC_HANDLER = 2
CLSCTX_LOCAL_SERVER = 4

CLSCTX_INPROC = 3 # Variable c_int
CLSCTX_SERVER = 5 # Variable c_int
CLSCTX_ALL = 7 # Variable c_int

CLSCTX_INPROC_SERVER16 = 8
CLSCTX_REMOTE_SERVER = 16
CLSCTX_INPROC_HANDLER16 = 32
CLSCTX_RESERVED1 = 64
CLSCTX_RESERVED2 = 128
CLSCTX_RESERVED3 = 256
CLSCTX_RESERVED4 = 512
CLSCTX_NO_CODE_DOWNLOAD = 1024
CLSCTX_RESERVED5 = 2048
CLSCTX_NO_CUSTOM_MARSHAL = 4096
CLSCTX_ENABLE_CODE_DOWNLOAD = 8192
CLSCTX_NO_FAILURE_LOG = 16384
CLSCTX_DISABLE_AAA = 32768
CLSCTX_ENABLE_AAA = 65536
CLSCTX_FROM_DEFAULT_CONTEXT = 131072

tagCLSCTX = c_int # enum
CLSCTX = tagCLSCTX

################################################################
ole32 = oledll.ole32
# Still experimenting with COM shutdown without crashes...

ole32.CoInitialize(None)

class _Cleaner(object):
    def __del__(self, func=ole32.CoUninitialize):
        # Sometimes, CoUnititialize, running at Python shutdown, raises an exception.
        # We suppress this when __debug__ is False.
        if __debug__:
            func()
        else:
            try: func()
            except WindowsError: pass

__cleaner = _Cleaner()
del _Cleaner

def _clean_exc_info():
    # the purpose of this function is to ensure that no com object
    # pointers are in sys.exc_info()
    try: 1//0
    except: pass

import atexit
atexit.register(_clean_exc_info)

################################################################
# The metaclasses...

class _cominterface_meta(type):
    # Metaclass for COM interface classes.
    # Creates POINTER(cls) also for the newly created class.
    def __new__(self, name, bases, namespace):
        methods = namespace.pop("_methods_", None)
        cls = type.__new__(self, name, bases, namespace)
        # XXX ??? First assign the _methods_, or first create the POINTER class?
        # or does it not matter?
        if methods is not None:
            setattr(cls, "_methods_", methods)

        # If we sublass a COM interface, for example:
        # class IDispatch(IUnknown):
        #     ....
        # then we want (need?) that
        # POINTER(IDispatch) is a subclass of POINTER(IUnknown).
        if bases == (object,):
            _ptr_bases = (cls, _compointer_base)
        else:
            _ptr_bases = (cls, POINTER(bases[0]))
        # The interface 'cls' is used as a mixin.
        # XXX "POINTER(<interface>)" looks nice as class name, but is it ok?
        p = type(_compointer_base)("POINTER(%s)" % cls.__name__,
                                   _ptr_bases,
                                   {})
        from ctypes import _pointer_type_cache
        _pointer_type_cache[cls] = p
        return cls

    def __setattr__(self, name, value):
        type.__setattr__(self, name, value)
        if name != "_methods_":
            return
        self._make_methods(value)

    def __get_baseinterface_methodcount(self):
        "Return the number of com methods in the base interfaces"
        return sum([len(itf.__dict__.get("_methods_", ()))
                    for itf in self.__mro__[1:]])

    def _make_methods(self, methods):
        # we insist on an _iid_ in THIS class!
        try:
            self.__dict__["_iid_"]
        except KeyError:
            raise AttributeError, "must define _iid_"
        vtbl_offset = self.__get_baseinterface_methodcount()

        getters = {}
        setters = {}

        # create low level, and maybe high level, COM method implementations.
        for i, item in enumerate(methods):
            restype, name, argtypes, paramflags, idlflags, doc = item
            # the function prototype
            prototype = WINFUNCTYPE(restype, *argtypes)
            # function calling the COM method slot
            func = prototype(i + vtbl_offset, name, paramflags)
            func.__doc__ = doc
            # and an unbound method, so we don't have to pass 'self'
            mth = new.instancemethod(func, None, self)

            # is it a property set or property get?
            is_prop = False
            # The following code assumes that the docstrings for
            # propget and propput are identical.
            if "propget" in idlflags:
                assert name.startswith("_get_")
                propname = name[len("_get_"):]
                getters[propname, doc, len(argtypes)] = func
                is_prop = True
            elif "propput" in idlflags:
                assert name.startswith("_set_")
                propname = name[len("_set_"):]
                setters[propname, doc, len(argtypes)] = func
                is_prop = True

            # We install the method in the class, except when it's a
            # property accessor.  And we make sure we don't overwrite
            # a property that's already present in the class.
            if not is_prop and not hasattr(self, name):
                setattr(self, name, mth)

            # attach it with a private name (__com_AddRef, for example),
            # so that custom method implementations can call it.
            mthname = "_%s__com_%s" % (self.__name__, name)
            setattr(self, mthname, mth)

        # create properties
        for item in set(getters.keys()) | set(getters.keys()):
            name, doc, nargs = item
            if nargs == 1:
                prop = property(getters.get(item), setters.get(item), doc=doc)
            else:
                # Hm, must be a descriptor where the __get__ method
                # returns a bound object having __getitem__ and
                # __setitem__ methods.
##                prop = named_property(getters.get(item), setters.get(item), doc=doc)
                raise "Not Yet Implemented"
            setattr(self, name, prop)
            
# metaclass for COM interface pointer classes
class _compointer_meta(type(c_void_p), _cominterface_meta):
    pass

# base class for COM interface pointer classes
class _compointer_base(c_void_p):
    __metaclass__ = _compointer_meta
    def __del__(self):
        "Release the COM refcount we own."
        if self: # calls __nonzero__
            self.Release()

    # Hm, shouldn't this be in c_void_p ?
    def __nonzero__(self):
        # get the .value property of the baseclass, this is the pointer value
        # both variants below do the same, and both are equally unreadable ;-)
        return bool(super(_compointer_base, self).value)
##        return bool(c_void_p.value.__get__(self))

    def __eq__(self, other):
        # COM identity rule
        #
        # XXX To compare COM interface pointers, should we
        # automatically QueryInterface for IUnknown on both items, and
        # compare the pointer values?
        if not isinstance(other, _compointer_base):
            return False
        # get the value property of the c_void_p baseclass, this is the pointer value
        return super(_compointer_base, self).value == super(_compointer_base, other).value

    # override the .value property of c_void_p
    #
    # for symmetry with other ctypes types
    # XXX explain
    # XXX check if really needed
    def __get_value(self):
        return self
    value = property(__get_value)

    def __repr__(self):
        return "<%s instance at %x>" % (self.__class__.__name__, id(self))

################################################################
# Memory mamagement of BSTR is broken.
#
# The way we do them here, it is not possible to transfer the
# ownership of a BSTR instance.  ctypes allocates the memory with
# SysAllocString if we call the constructor with a string, and the
# instance calls SysFreeString when it is destroyed.
# So BSTR's received from dll function calls will never be freed,
# and BSTR's we pass to functions are freed too often ;-(

from ctypes import _SimpleCData

class BSTR(_SimpleCData):
    _type_ = "X"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

def STDMETHOD(restype, name, argtypes=()):
    "Specifies a COM method slot"
    # restype, name, argtypes, paramflags, idlflags, docstring
    return restype, name, argtypes, None, (), None

PARAMFLAGS = {
    "in": 1,
    "out": 2,
    "retval": 8,
    }


class helpstring(object):
    def __init__(self, text):
        self.text = text

def encode_idl(names):
    # sum up all values found in PARAMFLAGS, ignoring all others.
    result = sum([PARAMFLAGS.get(n, 0) for n in names])
    return result & 3 # that's what _ctypes accept

def COMMETHOD2(idlflags, restype, methodname, *argspec):
    paramflags = []
    argtypes = []

    def unpack(idl, typ, name=None):
        return idl, typ, name

    # collect all helpstring instances
    helptext = [t.text for t in idlflags if isinstance(t, helpstring)]
    # join them together(does this make sense?) and replace by None if empty.
    helptext = "".join(helptext) or None

    for item in argspec:
        idl, typ, argname = unpack(*item)
        paramflags.append((encode_idl(idl), argname))
        argtypes.append(typ)
    if "propget" in idlflags:
        methodname = "_get_%s" % methodname
    elif "propput" in idlflags:
        methodname = "_put_%s" % methodname
    return restype, methodname, tuple(argtypes), tuple(paramflags), tuple(idlflags), helptext

################################################################

class IUnknown(object):
    __metaclass__ = _cominterface_meta
    _iid_ = GUID("{00000000-0000-0000-C000-000000000046}")

    _methods_ = [
        STDMETHOD(HRESULT, "QueryInterface",
                  [POINTER(GUID), POINTER(c_void_p)]),
        STDMETHOD(c_ulong, "AddRef"),
        STDMETHOD(c_ulong, "Release")
    ]

    def QueryInterface(self, interface, iid=None):
        "QueryInterface(klass) -> instance"
        p = POINTER(interface)()
        if iid is None:
            iid = interface._iid_
        self.__com_QueryInterface(byref(iid), byref(p))
        return p

    # these are only so that they get a docstring.
    # XXX There should be other ways to install a docstring.
    def AddRef(self):
        "Increase the internal refcount by one"
        return self.__com_AddRef()

    def Release(self):
        "Decrease the internal refcount by one"
        return self.__com_Release()

################################################################

##@stdcall(HRESULT, 'ole32',
##         [POINTER(IID), POINTER(IUnknown), c_ulong,
##          POINTER(IID), POINTER(c_void_p)])
def CoCreateInstance(clsid, interface=IUnknown, clsctx=CLSCTX_ALL, punkouter=None):
    p = POINTER(interface)()
    iid = interface._iid_
    CoCreateInstance._api_(byref(clsid), punkouter, clsctx, byref(iid), byref(p))
    return p
CoCreateInstance = stdcall(HRESULT, 'ole32',
                           [POINTER(IID), POINTER(IUnknown), c_ulong,
                            POINTER(IID), POINTER(c_void_p)]) (CoCreateInstance)

################################################################

################
##class CoClass(object):
##    # creation, and so on

##    def create_instance(self):
##        p = POINTER(self._com_interfaces_[0])()
##        oledll.ole32.CoCreateInstance(byref(self._clsid_),
##                                      None,
##                                      7, # CLSCTX
##                                      byref(p._iid_),
##                                      byref(p))
##        return p

################
##class IErrorInfo(IUnknown):
##    _iid_ = GUID("{1CF2B120-547D-101B-8E65-08002B2BD119}")
##    _methods_ = [
##        # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 5186
##        STDMETHOD(HRESULT, 'GetGUID', [POINTER(GUID)]),
##        STDMETHOD(HRESULT, 'GetSource', [POINTER(BSTR)]),
##        STDMETHOD(HRESULT, 'GetDescription', [POINTER(BSTR)]),
##        STDMETHOD(HRESULT, 'GetHelpFile', [POINTER(BSTR)]),
##        STDMETHOD(HRESULT, 'GetHelpContext', [POINTER(DWORD)]),
##    ]

################
##class ISupportErrorInfo(IUnknown):
##    _iid_ = GUID("{DF0B3D60-548F-101B-8E65-08002B2BD119}")
##    _methods_ = [
##        # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 5546
##        STDMETHOD(HRESULT, 'InterfaceSupportsErrorInfo', [POINTER(IID)]),
##    ]

__all__ = ["CoClass", "IUnknown", "GUID", "HRESULT", "BSTR", "STDMETHOD"]
