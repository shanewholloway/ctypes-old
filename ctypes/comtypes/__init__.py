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
    # Creates also a POINTER type for the newly created class.
    def __new__(self, name, bases, namespace):
        methods = namespace.pop("_methods_", None)
        cls = type.__new__(self, name, bases, namespace)
        if methods is not None:
            setattr(cls, "_methods_", methods)

        # If we sublass a COM interface, for example:
        #
        # class IDispatch(IUnknown):
        #     ....
        #
        # then we need to make sure that POINTER(IDispatch) is a
        # subclass of POINTER(IUnknown) because of the way ctypes
        # typechecks work.
        if bases == (object,):
            _ptr_bases = (cls, _compointer_base)
        else:
            _ptr_bases = (cls, POINTER(bases[0]))
        # The interface 'cls' is used as a mixin.
        p = type(_compointer_base)("POINTER(%s)" % cls.__name__,
                                   _ptr_bases,
                                   {})
        from ctypes import _pointer_type_cache
        _pointer_type_cache[cls] = p
        return cls

    def __setattr__(self, name, value):
        if name == "_methods_":
            self._make_methods(value)
        type.__setattr__(self, name, value)

    def __get_baseinterface_methodcount(self):
        "Return the number of com methods in the base interfaces"
        try:
            return sum([len(itf.__dict__["_methods_"])
                        for itf in self.__mro__[1:-1]])
        except KeyError, (name,):
            if name == "_methods_":
                raise TypeError, "baseinterface '%s' has no _methods_" % itf.__name__
            raise

    def _make_methods(self, methods):
        # we insist on an _iid_ in THIS class!
        try:
            self.__dict__["_iid_"]
        except KeyError:
            raise AttributeError, "must define _iid_"
        vtbl_offset = self.__get_baseinterface_methodcount()

        getters = {}
        setters = {}

        # create private low level, and public high level methods
        for i, item in enumerate(methods):
            restype, name, argtypes, paramflags, idlflags, doc = item
            # the function prototype
            prototype = WINFUNCTYPE(restype, *argtypes)

            # a low level unbound method calling the com method.
            # attach it with a private name (__com_AddRef, for example),
            # so that custom method implementations can call it.
            raw_func = prototype(i + vtbl_offset, name)
            setattr(self,
                    "_%s__com_%s" % (self.__name__, name),
                    new.instancemethod(raw_func, None, self))

            # a high level function calling the COM method
            func = prototype(i + vtbl_offset, name, paramflags)
            func.__doc__ = doc
            # make it an unbound method, so we don't have to pass 'self'
            mth = new.instancemethod(func, None, self)

            # is it a property set or property get?
            is_prop = False

            # XXX Hm.  What, when paramflags is None?
            # Or does have '0' values?
            # Seems we loose then, at least for properties...

            # The following code assumes that the docstrings for
            # propget and propput are identical.
            if "propget" in idlflags:
                assert name.startswith("_get_")
                nargs = len([flags for flags in paramflags
                             if flags[0] & 1])
                propname = name[len("_get_"):]
                getters[propname, doc, nargs] = func
                is_prop = True
            elif "propput" in idlflags:
                assert name.startswith("_set_")
                nargs = len([flags for flags in paramflags
                              if flags[0] & 1]) - 1
                propname = name[len("_set_"):]
                setters[propname, doc, nargs] = func
                is_prop = True

            # We install the method in the class, except when it's a
            # property accessor.  And we make sure we don't overwrite
            # a property that's already present in the class.
            if not is_prop:
                if hasattr(self, name):
                    setattr(self, "_" + name, mth)
                else:
                    setattr(self, name, mth)

        # create public properties / attribute accessors
        for item in set(getters.keys()) | set(getters.keys()):
            name, doc, nargs = item
            if nargs == 0:
                prop = property(getters.get(item), setters.get(item), doc=doc)
            else:
                # Hm, must be a descriptor where the __get__ method
                # returns a bound object having __getitem__ and
                # __setitem__ methods.
                prop = named_property(getters.get(item), setters.get(item), doc=doc)
            # Again, we should not overwrite class attributes that are
            # already present.
            if hasattr(self, name):
                setattr(self, "_" + name, prop)
            else:
                setattr(self, name, prop)

class bound_named_property(object):
    def __init__(self, getter, setter, im_inst):
        self.im_inst = im_inst
        self.getter = getter
        self.setter = setter

    def __getitem__(self, index):
        if self.getter is None:
            raise TypeError("unsubscriptable object")
        return self.getter(self.im_inst, index)

    def __setitem__(self, index, value):
        if self.setter is None:
            raise TypeError("object does not support item assignment")
        self.setter(self.im_inst, index, value)

class named_property(object):
    def __init__(self, getter, setter, doc):
        self.getter = getter
        self.setter = setter
        self.doc = doc

    def __get__(self, im_inst, im_class=None):
        if im_inst is None:
            return self
        return bound_named_property(self.getter, self.setter, im_inst)

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

from ctypes import _SimpleCData

class BSTR(_SimpleCData):
    _type_ = "X"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

################################################################

class helpstring(object):
    def __init__(self, text):
        self.text = text

class defaultvalue(object):
    def __init__(self, value):
        self.value = value

################################################################

PARAMFLAGS = {
    "in": 1,
    "out": 2,
    "retval": 8,
    }

def encode_idl(names):
    # sum up all values found in PARAMFLAGS, ignoring all others.
    result = sum([PARAMFLAGS.get(n, 0) for n in names])
    return result & 3 # that's what _ctypes accept

def COMMETHOD(idlflags, restype, methodname, *argspec):
    "Specifies a COM method slot with idlflags"
    paramflags = []
    argtypes = []

    def unpack(idl, typ, name=None):
        return idl, typ, name

    # collect all helpstring instances
    helptext = [t.text for t in idlflags if isinstance(t, helpstring)]
    # join them together(does this make sense?) and replace by None if empty.
    helptext = "".join(helptext) or None

    # XXX some thoughts:
    #
    # In _ctypes.c::_get_one(), it is difficult to decide what to do.
    #
    # The _get_one() function is called for each [out] parameter, with
    # an instance of a ctypes type.  The argument 'type' we have in
    # paramflags is actually a POINTER to this type.
    #
    # What are the possibilities, what are the problems?
    #
    # 1. Simple, intergral, non-pointer data type: call the type's
    # stgdict->getfunc() to build the result.  stgdict->proto in this
    # case is a one character Python string containing the type tag
    # from the formattable.
    # Sample:
    #    def Get(self):
    #        temp = c_int()
    #        self.__com_Get(byref(temp))
    #        return temp.value
    #
    # 1a. Same as before, but an instance that owns some resources,
    # like BSTR.  We have to call SysFreeString() to free the resources.
    # Sample:
    #    def Get(self):
    #        temp = BSTR()
    #        self.__com_Get(byref(temp))
    #        temp2 = temp.value
    #        temp._free_resources_()
    #        return temp2
    #
    # 1b. A structure, like VARIANT, that actually represents an
    # integral data type. Again, we should return it's .value
    # attribute, and, as in 1a, we have to call VariantClear() to free
    # resources.  Sample code same as in 1a.
    #
    # 2. POINTER to cominterface: In this case we would like _get_one()
    # to return the result itself.
    # Sample:
    #    def Get(self):
    #        temp = POINTER(IUnknown)()
    #        self.__com_Get(byref(temp))
    #        return temp
    #
    # Exactly here in the code is at least ONE place where all this
    # info is available, and we can execute arbitrary complicated
    # Python code much easier than in C.
    #
    # We could pass simple info (in form of integer flags) to
    # _ctypes.c in the paramflags tuple (there are a lots of bits
    # unused in the PARAMFLAGS enum), but complicated stuff would also
    # be possible.
    #
    # Another possibility would be to have this info in the types itself.
    # Something like _from_outarg_.
    #
    for item in argspec:
        idl, typ, argname = unpack(*item)
        pflags = encode_idl(idl)
        if 2 & pflags:
            rettype = typ._type_
        paramflags.append((pflags, argname))
        argtypes.append(typ)
    if "propget" in idlflags:
        methodname = "_get_%s" % methodname
    elif "propput" in idlflags:
        methodname = "_set_%s" % methodname
    return restype, methodname, tuple(argtypes), tuple(paramflags), tuple(idlflags), helptext

def STDMETHOD(restype, name, argtypes=()):
    "Specifies a COM method slot without idlflags"
    # restype, name, argtypes, paramflags, idlflags, docstring
    return restype, name, argtypes, None, (), None

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
