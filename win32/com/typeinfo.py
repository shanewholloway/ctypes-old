from ctypes.com import IUnknown, COMPointer, GUID, REFIID, REFGUID, \
     PPUNK, PUNK, STDMETHOD

from ctypes.com import HRESULT, STDMETHOD

from ctypes import Structure, Union, POINTER, byref, oledll, \
     c_short, c_ushort, c_int, c_uint, c_long, c_ulong, c_wchar_p, c_voidp, \
     c_float, c_double, c_byte, c_ubyte

from ctypes import sizeof

oleaut32 = oledll.oleaut32

DWORD = c_ulong
WORD = c_ushort

################################################################
# Interfaces declarations
#
def _mth(*args):
    return args

# fake
from ctypes.com import IUnknownPointer
ITypeCompPointer = IUnknownPointer
ITypeComp = IUnknown

LPOLESTR = c_wchar_p

HREFTYPE = c_ulong

class ITypeInfo(IUnknown):
    _iid_ = GUID("{00020401-0000-0000-C000-000000000046}")
                 
class ITypeInfoPointer(COMPointer):
    _interface_ = ITypeInfo

class ITypeLib(IUnknown):
    _iid_ = GUID("{00020402-0000-0000-C000-000000000046}")

class ITypeLibPointer(IUnknownPointer):
    _interface_ = ITypeLib

class IDispatch(IUnknown):
    _iid_ = GUID("{00020400-0000-0000-C000-000000000046}")

class IDispatchPointer(COMPointer):
    _interface_ = IDispatch

################################################################
# constants
#
TKIND_ENUM = 0
TKIND_RECORD = 1
TKIND_MODULE = 2
TKIND_INTERFACE = 3
TKIND_DISPATCH = 4
TKIND_COCLASS = 5
TKIND_ALIAS = 6
TKIND_UNION = 7

DISPATCH_METHOD = 0x1
DISPATCH_PROPERTYGET = 0x2
DISPATCH_PROPERTYPUT = 0x4
DISPATCH_PROPERTYPUTREF = 0x8

##VARKIND enumeration
VAR_PERINSTANCE = 0
VAR_STATIC = 1
VAR_CONST = 2
VAR_DISPATCH = 3

################################################################
# typeinfo, typelib and automation data types
#
DISPID = c_long
MEMBERID = DISPID
TYPEKIND = c_int # enum

################################################################
# I don't know if it's possible to do BSTR correctly.
#
# For debugging BSTR memory leaks, see
# http://www.distobj.com/comleaks.htm
#  and
# http://support.microsoft.com/default.aspx?scid=KB;en-us;q139071
# Q139071
#
# Apparently the debug version of the ole libraries is no longer
# required starting with windows 2000, and we could implement
# IMallocSpy in Python.
################################################################

##class BSTR(Union):
##    _fields_ = [("_ptr", c_int),
##                ("value", c_wchar_p)]

##    def __init__(self, text=None, SysAllocString=oleaut32.SysAllocString):
##        if text is not None:
##            self._ptr = SysAllocString(unicode(text))

##    # Blush, of course (it should depend on param)
##    def from_param(cls, param):
##        return cls(param)
##    from_param = classmethod(from_param)

##    def _as_parameter_(self):
##        return self._ptr
##    _as_parameter_ = property(_as_parameter_)

##    def __repr__(self):
##        if self._ptr:
##            return "<BSTR '%s'>" % self.value
##        else:
##            return "<BSTR (NULL)>"

##    def __del__(self, SysFreeString=oleaut32.SysFreeString):
##        if self._ptr:
##            SysFreeString(self._ptr)
##            self._ptr = 0

### XXX BUG: Crashed hard when _ptr set to 0
####            self._ptr = 0

from _ctypes import _SimpleCData

class BSTR(_SimpleCData):
    _type_ = "X"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

assert(sizeof(BSTR) == 4)

# VARTYPE is unsigned short!
VARTYPE = c_ushort
SCODE = DWORD


#fake it, in reality it's a union having 16 bytes
class VARIANT(Structure):
    class U(Union):
        _fields_ = [("bVal", c_byte),
                    ("iVal", c_int),
                    ("lVal", c_long),
                    ("fltVal", c_float),
                    ("dblVal", c_double),
                    ("boolVal", c_int),
                    ("strVal", c_wchar_p), # XXX ???
                    # ...
                    ("pUnkVal", IUnknownPointer),
                    ("pDispVal", IDispatchPointer),
                    ]

    _fields_ = [("vt", VARTYPE),
                ("wReserved1", c_ushort),
                ("wReserved2", c_ushort),
                ("wReserved3", c_ushort),
                ("_", U)]

    def __repr__(self):
        return "<VARIANT %d at %x>" % (self.vt, id(self))

    def get_value(self, type=None):
        var = VARIANT()
        if type is None:
            type = self.vt
        vt, field = TypeToVT[type]
        oleaut32.VariantChangeType(byref(var), byref(self),
                                   0, vt)
        return getattr(var._, field)
assert(sizeof(VARIANT) == 16)

class DISPPARAMS(Structure):
    _fields_ = [("rgvarg", POINTER(VARIANT)),
                ("rgdispidNamedArgs", POINTER(DISPID)),
                ("cArgs", c_uint),
                ("cNamedArgs", c_uint)]
assert(sizeof(DISPPARAMS) == 16)

# c:/vc98/include/oaidl.h

class EXCEPINFO(Structure):
    _fields_ = [("wCode", c_ushort),
                ("wReserved", c_ushort),
                ("bstrSource", BSTR),
                ("bstrDescription", BSTR),
                ("bstrHelpFile", BSTR),
                ("dwHelpContext", DWORD),
                ("pvReserved", c_voidp),
                ("pfnDeferredFillIn", c_int), # XXX
                ("scode", SCODE)]
assert(sizeof(EXCEPINFO) == 32)

LCID = c_ulong
SYSKIND = c_int # enu
HREFTYPE = c_ulong

class TLIBATTR(Structure):
    _fields_ = [("guid", GUID),
                ("lcid", LCID),
                ("syskind", SYSKIND),
                ("wMajorVersionNum", WORD),
                ("wMinorVersionNum", WORD),
                ("wLibFlags", WORD)]
assert(sizeof(TLIBATTR) == 32), sizeof(TLIBATTR)

class PARAMDESCEX(Structure):
    _fields_ = [("cBytes", c_ulong),
                ("varDefaultValue", VARIANT)]
assert(sizeof(PARAMDESCEX) == 24)
    
class PARAMDESC(Structure):
    _fields_ = [("pPARAMDescEx", POINTER(PARAMDESCEX)),
                ("wPARAMFlags", WORD)]
assert sizeof(PARAMDESC) == 8

LPTYPEDESC = POINTER("TYPEDESC")

class TYPEDESC(Structure):
    class U(Union):
        _fields_ = [("lptdesc", LPTYPEDESC),
##                    ("lpadesc", POINTER(ARRAYDESC)),
                    ("hreftype", HREFTYPE)]
    _fields_ = [("u", U),
                ("vt", VARTYPE)]
assert(sizeof(TYPEDESC) == 8), sizeof(TYPEDESC)

LPTYPEDESC.set_type(TYPEDESC)

class IDLDESC(Structure):
    _fields_ = [("dwReserved", c_ulong),
                ("wIDLFlags", c_ushort)]
assert(sizeof(IDLDESC) == 8)

class TYPEATTR(Structure):
    _fields_ = [("guid", GUID),
                ("lcid", LCID),
                ("dwReserved", c_ulong),
                ("memidConstructor", MEMBERID),
                ("memidDestructor", MEMBERID),
                ("lpstrSchema", c_wchar_p),
                ("cbSizeInstance", c_ulong),
                ("typekind", TYPEKIND),
                ("cFuncs", c_ushort),
                ("cVars", c_ushort),
                ("cImplTypes", c_ushort),
                ("cbSizeVft", c_ushort),
                ("cbAlignment", c_ushort),
                ("wTypeFlags", c_ushort),
                ("wMajorVerNum", c_ushort),
                ("wMinorVerNum", c_ushort),
                ("tdescAlias", TYPEDESC),
                ("idldescType", IDLDESC),
                ]
LPTYPEATTR = POINTER(TYPEATTR)
assert(sizeof(TYPEATTR) == 76)

class ELEMDESC(Structure):
    _fields_ = [("tdesc", TYPEDESC),
                ("paramdesc", PARAMDESC)]
assert(sizeof(ELEMDESC) == 16)

VARKIND = c_int # enum

class VARDESC(Structure):
    class U(Union):
        _fields_ = [("oInst", c_ulong),
                    ("lpvarValue", POINTER(VARIANT))]
    _fields_ = [("memid", MEMBERID),
                ("strSchema", c_wchar_p),
                ("u", U),
                ("elemdescVar", ELEMDESC),
                ("wVarFlags", c_ushort),
                ("varkind", VARKIND)]
LPVARDESC = POINTER(VARDESC)
assert(sizeof(VARDESC) == 36)

FUNCKIND = c_int # enum
INVKIND = c_int # enum
CALLCONV = c_int # enum

class FUNCDESC(Structure):
    _fields_ = [("memid", MEMBERID),
                ("lprgscode", POINTER(SCODE)),
                ("lprgelemdescParam", POINTER(ELEMDESC)),
                ("funckind", FUNCKIND),
                ("invkind", INVKIND),
                ("callconv", CALLCONV),
                ("cParams", c_short),
                ("cParamsOpt", c_short),
                ("oVft", c_short),
                ("cScodes", c_short),
                ("elemdescFunc", ELEMDESC),
                ("wFuncFlags", WORD)]
LPFUNCDESC = POINTER(FUNCDESC)
assert(sizeof(FUNCDESC) == 52), sizeof(FUNCDESC)

################################################################
# The interfaces COM methods

IMPLTYPEFLAGS = c_int

IMPLTYPEFLAG_FDEFAULT   = 0x1
IMPLTYPEFLAG_FSOURCE      = 0x2
IMPLTYPEFLAG_FRESTRICTED   = 0x4
IMPLTYPEFLAG_FDEFAULTVTABLE   = 0x8

ITypeInfo._methods_ = [
    STDMETHOD(HRESULT, "GetTypeAttr", POINTER(LPTYPEATTR)),
    STDMETHOD(HRESULT, "GetTypeComp", POINTER(ITypeCompPointer)),
    STDMETHOD(HRESULT, "GetFuncDesc", c_uint,  POINTER(POINTER(FUNCDESC))),
    STDMETHOD(HRESULT, "GetVarDesc", c_uint, POINTER(POINTER(VARDESC))),
    STDMETHOD(HRESULT, "GetNames", MEMBERID, POINTER(BSTR), c_uint, POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetRefTypeOfImplType", c_uint, POINTER(HREFTYPE)),
    STDMETHOD(HRESULT, "GetImplTypeFlags", c_uint, POINTER(IMPLTYPEFLAGS)),
    STDMETHOD(HRESULT, "GetIDsOfNames", POINTER(LPOLESTR), c_uint, POINTER(c_int)),
    STDMETHOD(HRESULT, "Invoke", PUNK, MEMBERID, WORD, POINTER(DISPPARAMS),
              POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetDocumentation", MEMBERID, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ulong), POINTER(BSTR)),
    STDMETHOD(HRESULT, "GetDllEntry", MEMBERID, c_int, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ushort)),
    STDMETHOD(HRESULT, "GetRefTypeInfo", HREFTYPE, POINTER(ITypeInfoPointer)),
    STDMETHOD(HRESULT, "AddressOfMember", MEMBERID, c_int, POINTER(c_voidp)),
    STDMETHOD(HRESULT, "CreateInstance", c_voidp, REFIID, PPUNK),
    STDMETHOD(HRESULT, "GetMops", MEMBERID, POINTER(BSTR)),
    STDMETHOD(HRESULT, "GetContainingTypeLib", POINTER(ITypeLibPointer), POINTER(c_uint)),
    STDMETHOD(HRESULT, "ReleaseTypeAttr", LPTYPEATTR),
    STDMETHOD(HRESULT, "ReleaseFuncDesc", LPFUNCDESC),
    STDMETHOD(HRESULT, "ReleaseVarDesc", LPVARDESC)]

ITypeLib._methods_ = [
    STDMETHOD(c_uint, "GetTypeInfoCount"),
    STDMETHOD(HRESULT, "GetTypeInfo", c_uint, POINTER(ITypeInfoPointer)),
    STDMETHOD(HRESULT, "GetTypeInfoType", c_int, POINTER(TYPEKIND)),
    STDMETHOD(HRESULT, "GetTypeInfoOfGuid", REFGUID, POINTER(ITypeInfoPointer)),
    STDMETHOD(HRESULT, "GetLibAttr", POINTER(TLIBATTR)),
    STDMETHOD(HRESULT, "GetTypeComp", POINTER(ITypeComp)),
    STDMETHOD(HRESULT, "GetDocumentation", c_int, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ulong), POINTER(BSTR)),
    STDMETHOD(HRESULT, "IsName", c_wchar_p, c_ulong, c_int),
    STDMETHOD(HRESULT, "FindName", c_wchar_p, c_ulong, POINTER(ITypeInfoPointer),
              POINTER(MEMBERID), POINTER(c_uint)),
    STDMETHOD(HRESULT, "ReleaseTLibAttr", POINTER(TLIBATTR))]

IDispatch._methods_ = [
    STDMETHOD(HRESULT, "GetTypeInfoCount", POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetTypeInfo", c_uint, LCID, POINTER(ITypeInfoPointer)),
    STDMETHOD(HRESULT, "GetIDsOfNames", REFIID, POINTER(c_wchar_p), c_uint,
              LCID, POINTER(DISPID)),
    STDMETHOD(HRESULT, "Invoke", DISPID, REFIID, LCID, WORD, POINTER(DISPPARAMS),
              POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(c_uint))]

################################################################
# functions
#

REGKIND_DEFAULT = 0
REGKIND_REGISTER = 1
REGKIND_NONE = 2

def LoadTypeLib(fnm):
    p = ITypeLibPointer()
    oleaut32.LoadTypeLib(unicode(fnm), byref(p))
    return p

def LoadTypeLibEx(fnm, regkind=REGKIND_NONE):
    p = ITypeLibPointer()
    oleaut32.LoadTypeLibEx(unicode(fnm), regkind, byref(p))
    return p
    

if __name__ == '__main__':
    def GetComRefcount(p):
        p.AddRef()
        return p.Release()

    path = r"c:\tss5\bin\debug\ITInfo.dll"
    p = LoadTypeLibEx(path)
    print p, "refcount", GetComRefcount(p)

    p2 = IUnknownPointer()
    p.QueryInterface(byref(p2._interface_._iid_),
                     byref(p2))
    print p2, "refcount", GetComRefcount(p)
    print p, "refcount", GetComRefcount(p)
    del p2

    print p, "refcount", GetComRefcount(p)
