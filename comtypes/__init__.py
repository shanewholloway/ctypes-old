# requires ctypes 0.9.3 or later
import new
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

from _ctypes import CFuncPtr as _CFuncPtr, FUNCFLAG_STDCALL as _FUNCFLAG_STDCALL
from ctypes import _win_functype_cache

# For backward compatibility, the signature of WINFUNCTYPE cannot be
# changed, so we have to add this - which is basically the same, but
# allows to specify parameter flags from the win32 PARAMFLAGS
# enumeration.  Maybe later we have to add optional default parameter
# values and parameter names as well.
def COMMETHODTYPE(restype, argtypes, paramflags):
    flags = paramflags
    try:
        return _win_functype_cache[(restype, argtypes, flags)]
    except KeyError:
        class WinFunctionType(_CFuncPtr):
            _argtypes_ = argtypes
            _restype_ = restype
            _flags_ = _FUNCFLAG_STDCALL
            parmflags = flags
        _win_functype_cache[(restype, argtypes, flags)] = WinFunctionType
        return WinFunctionType

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
        if methods:
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
        # we insist on an _iid_ in THIS class"
        try:
            self.__dict__["_iid_"]
        except KeyError:
            raise AttributeError, "must define _iid_"
        vtbl_offset = self.__get_baseinterface_methodcount()
        for i, (restype, name, argtypes) in enumerate(methods):
            # the function prototype
            prototype = WINFUNCTYPE(restype, *argtypes)
            mth = prototype(i + vtbl_offset, name)
            mth = new.instancemethod(mth, None, self)
            impl = getattr(self, name, None)
            if impl is None:
                # don't overwrite a custom implementation
                setattr(self, name, mth)
            # attach it with a private name (__com_AddRef, for example)
            mthname = "_%s__com_%s" % (self.__name__, name)
            setattr(self, mthname, mth)

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
        # get the value property of the baseclass, this is the pointer value
        # both variants below do the same, and both are equally unreadable ;-)
        return bool(super(_compointer_base, self).value)
##        return bool(c_void_p.value.__get__(self))

    def __eq__(self, other):
        # COM identity rule
        if not isinstance(other, _compointer_base):
            return False
        # get the value property of the c_void_p baseclass, this is the pointer value
        return super(_compointer_base, self).value == super(_compointer_base, other).value

    # override the .value property of c_void_p
    #
    # for symmetry with other ctypes types
    # XXX explain
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
    return restype, name, argtypes

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
