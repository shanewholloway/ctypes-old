"""create and manipulate C data types in Python"""

# special developer support to use ctypes from the CVS sandbox,
# without installing it
import os, sys
_magicfile = os.path.join(os.path.dirname(__file__), ".CTYPES_DEVEL")
if os.path.isfile(_magicfile):
    execfile(_magicfile)
del os, _magicfile

__version__ = "0.6.3"

from _ctypes import Union, Structure, Array
from _ctypes import _Pointer
from _ctypes import CFuncPtr as _CFuncPtr

import os as _os

if _os.name == "nt":
    from _ctypes import FormatError

from _ctypes import FUNCFLAG_CDECL as _FUNCFLAG_CDECL

"""
WINOLEAPI -> HRESULT
WINOLEAPI_(type)

STDMETHODCALLTYPE

STDMETHOD(name)
STDMETHOD_(type, name)

STDAPICALLTYPE
"""

def c_buffer(init, size=None):
    """c_buffer(aString) -> character array
    c_buffer(anInteger) -> character array
    c_buffer(aString, anInteger) -> character array
    """
    if isinstance(init, str):
        if size is None:
            size = len(init)+1
        buftype = c_char * size
        buf = buftype()
        buf.value = init
        return buf
    elif isinstance(init, (int, long)):
        buftype = c_char * init
        buf = buftype()
        return buf
    raise TypeError, init


def CFUNCTYPE(restype, *argtypes):
    class CFunctionType(_CFuncPtr):
        _argtypes_ = argtypes
        _restype_ = restype
        _flags_ = _FUNCFLAG_CDECL
    return CFunctionType

if _os.name == "nt":
    from _ctypes import LoadLibrary as _LoadLibrary, \
         FreeLibrary as _FreeLibrary
    from _ctypes import FUNCFLAG_HRESULT as _FUNCFLAG_HRESULT, \
         FUNCFLAG_STDCALL as _FUNCFLAG_STDCALL

    def WINFUNCTYPE(restype, *argtypes):
        class WinFunctionType(_CFuncPtr):
            _argtypes_ = argtypes
            _restype_ = restype
            _flags_ = _FUNCFLAG_STDCALL
        return WinFunctionType

elif _os.name == "posix":
    from _ctypes import dlopen as _LoadLibrary
    _FreeLibrary = None

from _ctypes import sizeof, byref, addressof
from _ctypes import _SimpleCData

class c_short(_SimpleCData):
    _type_ = "h"
    def __repr__(self):
        return "c_short(%d)" % self.value

class c_ushort(_SimpleCData):
    _type_ = "H"
    def __repr__(self):
        return "c_ushort(%d)" % self.value

class c_int(_SimpleCData):
    _type_ = "i"
    def __repr__(self):
        return "c_int(%d)" % self.value

class c_uint(_SimpleCData):
    _type_ = "I"
    def __repr__(self):
        return "c_uint(%d)" % self.value
    
class c_long(_SimpleCData):
    _type_ = "l"
    def __repr__(self):
        return "c_long(%d)" % self.value

class c_ulong(_SimpleCData):
    _type_ = "L"
    def __repr__(self):
        return "c_ulong(%d)" % self.value
    
class c_float(_SimpleCData):
    _type_ = "f"
    def __repr__(self):
        return "%s(%f)" % (self.__class__.__name__, self.value)
    
class c_double(_SimpleCData):
    _type_ = "d"
    def __repr__(self):
        return "%s(%f)" % (self.__class__.__name__, self.value)
    
class c_longlong(_SimpleCData):
    _type_ = "q"
    def __repr__(self):
        return "c_longlong(%s)" % self.value

class c_ulonglong(_SimpleCData):
    _type_ = "Q"
    def __repr__(self):
        return "c_ulonglong(%s)" % self.value
##    def from_param(cls, val):
##        return ('d', float(val), val)
##    from_param = classmethod(from_param)

class c_ubyte(_SimpleCData):
    _type_ = "B"
    def __repr__(self):
        return "c_ubyte(%s)" % self.value
# backward compatibility:
##c_uchar = c_ubyte

class c_byte(_SimpleCData):
    _type_ = "b"
    def __repr__(self):
        return "c_byte(%s)" % self.value

class c_char(_SimpleCData):
    _type_ = "c"
    def __repr__(self):
        return "c_char(%r)" % self.value

class c_char_p(_SimpleCData):
    _type_ = "z"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

class c_void_p(_SimpleCData):
    _type_ = "P"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)
c_voidp = c_void_p # backwards compatibility (to a bug)

if _os.name == "nt":
    class c_wchar_p(_SimpleCData):
        _type_ = "Z"
        def __repr__(self):
            return "%s(%r)" % (self.__class__.__name__, self.value)

    class c_wchar(_SimpleCData):
        _type_ = "u"
        def __repr__(self):
            return "c_wchar(%r)" % self.value

# This cache maps types to pointers to them.
_pointer_type_cache = {}

def POINTER(cls):
    if type(cls) is str:
        klass = type(_Pointer)("LP_%s" % cls,
                               (_Pointer,),
                               {})
        _pointer_type_cache[id(klass)] = klass
        return klass
    klass = _pointer_type_cache.get(cls, None)
    if klass is None:
        name = "LP_%s" % cls.__name__
        klass = type(_Pointer)(name,
                               (_Pointer,),
                               {'_type_': cls})
        _pointer_type_cache[cls] = klass
    return klass
    
def SetPointerType(pointer, cls):
    if _pointer_type_cache.get(cls, None) is not None:
        raise RuntimeError, \
              "This type already exists in the cache"
    if not _pointer_type_cache.has_key(id(pointer)):
        raise RuntimeError, \
              "What's this???"
    pointer.set_type(cls)
    _pointer_type_cache[cls] = pointer
    del _pointer_type_cache[id(pointer)]


def pointer(inst):
    return POINTER(type(inst))(inst)

def ARRAY(typ, len):
    return typ * len

################################################################


class CDLL:
    class _CdeclFuncPtr(_CFuncPtr):
        _flags_ = _FUNCFLAG_CDECL
        _restype_ = c_int # default, can be overridden in instances

    _handle = 0
    def __init__(self, name, LoadLibrary=_LoadLibrary):
        self._name = name
        self._handle = LoadLibrary(self._name)

    def __repr__(self):
        return "<%s '%s', handle %x at %x>" % \
               (self.__class__.__name__, self._name,
                (self._handle & (sys.maxint*2 + 1)),
                id(self))

    def __getattr__(self, name):
        if name[:2] == '__' and name[-2:] == '__':
            raise AttributeError, name
        func = self._CdeclFuncPtr(name, self)
        setattr(self, name, func)
        return func

    def __getitem__(self, name):
        return getattr(self, name)

    def __del__(self, FreeLibrary=_FreeLibrary):
        if self._handle != 0 and FreeLibrary:
            FreeLibrary(self._handle)
        self._handle = 0

if _os.name ==  "nt":
        
    class WinDLL(CDLL):
        class _StdcallFuncPtr(_CFuncPtr):
            _flags_ = _FUNCFLAG_STDCALL
            _restype_ = c_int # default, can be overridden in instances

        def __getattr__(self, name):
            if name[:2] == '__' and name[-2:] == '__':
                raise AttributeError, name
            func = self._StdcallFuncPtr(name, self)
            setattr(self, name, func)
            return func


    class OleDLL(CDLL):
        class _OlecallFuncPtr(_CFuncPtr):
            _flags_ = _FUNCFLAG_STDCALL | _FUNCFLAG_HRESULT
            _restype_ = c_int # needed, but unused
        def __getattr__(self, name):
            if name[:2] == '__' and name[-2:] == '__':
                raise AttributeError, name
            func = self._OlecallFuncPtr(name, self)
            setattr(self, name, func)
            return func

class _DLLS:
    def __init__(self, dlltype):
        self._dlltype = dlltype
        
    def __getattr__(self, name):
        if name[0] == '_':
            raise AttributeError, name
        dll = self._dlltype(name)
        setattr(self, name, dll)
        return dll

    def __getitem__(self, name):
        return getattr(self, name)

    def LoadLibrary(self, name):
        return self._dlltype(name)

cdll = _DLLS(CDLL)
if _os.name == "nt":
    windll = _DLLS(WinDLL)
    oledll = _DLLS(OleDLL)

    GetLastError = windll.kernel32.GetLastError

    def WinError(code=None):
        if code is None:
            code = GetLastError()
        return WindowsError(code, FormatError(code).strip())
