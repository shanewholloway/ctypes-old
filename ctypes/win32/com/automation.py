from ctypes import *
from ctypes.com import IUnknown, GUID, REFIID, REFGUID, STDMETHOD, HRESULT, PIUnknown, COMObject
from ctypes.wintypes import DWORD, WORD

oleaut32 = oledll.oleaut32

################################################################
# types

LPOLESTR = c_wchar_p
HREFTYPE = c_ulong

VARTYPE = c_ushort
SCODE = DWORD

################################################################
# typeinfo, typelib and automation data types
#
DISPID = c_long
MEMBERID = DISPID
TYPEKIND = c_int # enum

LCID = c_ulong
SYSKIND = c_int # enu

FUNCKIND = c_int # enum
INVKIND = c_int # enum
CALLCONV = c_int # enum

IMPLTYPEFLAGS = c_int

################################################################
# constants
#
REGKIND_DEFAULT = 0
REGKIND_REGISTER = 1
REGKIND_NONE = 2

IMPLTYPEFLAG_FDEFAULT   = 0x1
IMPLTYPEFLAG_FSOURCE      = 0x2
IMPLTYPEFLAG_FRESTRICTED   = 0x4
IMPLTYPEFLAG_FDEFAULTVTABLE   = 0x8

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

VAR_PERINSTANCE = 0
VAR_STATIC = 1
VAR_CONST = 2
VAR_DISPATCH = 3

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

from _ctypes import _SimpleCData

class BSTR(_SimpleCData):
    _type_ = "X"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

assert(sizeof(BSTR) == 4)

################################################################
# Interfaces declarations
#

# fake
ITypeComp = IUnknown

class ITypeInfo(IUnknown):
    _iid_ = GUID("{00020401-0000-0000-C000-000000000046}")
                 
class ITypeLib(IUnknown):
    _iid_ = GUID("{00020402-0000-0000-C000-000000000046}")

class IDispatch(IUnknown):
    _iid_ = GUID("{00020400-0000-0000-C000-000000000046}")

################################################################
# VARIANT

TypeToVT = {
    3: (3, "iVal"),
    5: (5, "dblVal"),
    8: (8, "strVal"),
    11: (3, "iVal"),
    }

# XXX get_value must be improved. And should it be exposed as value property?
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
                    ("pUnkVal", POINTER(IUnknown)),
                    ("pDispVal", POINTER(IDispatch)),
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
        vt, field = TypeToVT.get(type, (None, None))
        if vt is None:
            return "(%d)" % type
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

class TLIBATTR(Structure):
    _fields_ = [("guid", GUID),
                ("lcid", LCID),
                ("syskind", SYSKIND),
                ("wMajorVerNum", WORD),
                ("wMinorVerNum", WORD),
                ("wLibFlags", WORD)]
assert(sizeof(TLIBATTR) == 32), sizeof(TLIBATTR)
LPTLIBATTR = POINTER(TLIBATTR)

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

# For CreateDispTypeInfo

##from ctypes import c_ushort, c_int, c_uint, c_long, c_wchar_p, Structure

##VARTYPE = c_int # enum
##DISPID = c_long
##CALLCONV = c_int

##class PARAMDATA(Structure):
##    _fields_ = [("szName", c_wchar_p),
##                ("vt", VARTYPE)]

##class METHODDATA(Structure):
##    _fields_ = [("szName", c_wchar_p),
##                ("ppdata", POINTER(PARAMDATA)),
##                ("dispid", DISPID),
##                ("iMeth", c_uint),
##                ("cc", CALLCONV),
##                ("cArgs", c_uint),
##                ("wFlags", c_ushort),
##                ("vtReturn", VARTYPE)]

##class INTERFACEDATA(Structure):
##    _fields_ = [("pmethdata", POINTER(METHODDATA)),
##                ("cMembers", c_uint)]


################################################################
# The interfaces COM methods

ITypeInfo._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "GetTypeAttr", POINTER(LPTYPEATTR)),
    STDMETHOD(HRESULT, "GetTypeComp", POINTER(POINTER(ITypeComp))),
    STDMETHOD(HRESULT, "GetFuncDesc", c_uint,  POINTER(POINTER(FUNCDESC))),
    STDMETHOD(HRESULT, "GetVarDesc", c_uint, POINTER(POINTER(VARDESC))),
    STDMETHOD(HRESULT, "GetNames", MEMBERID, POINTER(BSTR), c_uint, POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetRefTypeOfImplType", c_uint, POINTER(HREFTYPE)),
    STDMETHOD(HRESULT, "GetImplTypeFlags", c_uint, POINTER(IMPLTYPEFLAGS)),
    STDMETHOD(HRESULT, "GetIDsOfNames", POINTER(LPOLESTR), c_uint, POINTER(c_int)),
    STDMETHOD(HRESULT, "Invoke", PIUnknown, MEMBERID, WORD, POINTER(DISPPARAMS),
              POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetDocumentation", MEMBERID, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ulong), POINTER(BSTR)),
    STDMETHOD(HRESULT, "GetDllEntry", MEMBERID, c_int, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ushort)),
    STDMETHOD(HRESULT, "GetRefTypeInfo", HREFTYPE, POINTER(POINTER(ITypeInfo))),
    STDMETHOD(HRESULT, "AddressOfMember", MEMBERID, c_int, POINTER(c_voidp)),
    STDMETHOD(HRESULT, "CreateInstance", c_voidp, REFIID, POINTER(PIUnknown)),
    STDMETHOD(HRESULT, "GetMops", MEMBERID, POINTER(BSTR)),
    STDMETHOD(HRESULT, "GetContainingTypeLib", POINTER(POINTER(ITypeLib)), POINTER(c_uint)),
    STDMETHOD(HRESULT, "ReleaseTypeAttr", LPTYPEATTR),
    STDMETHOD(HRESULT, "ReleaseFuncDesc", LPFUNCDESC),
    STDMETHOD(HRESULT, "ReleaseVarDesc", LPVARDESC)]

ITypeLib._methods_ = IUnknown._methods_ + [
    STDMETHOD(c_uint, "GetTypeInfoCount"),
    STDMETHOD(HRESULT, "GetTypeInfo", c_uint, POINTER(POINTER(ITypeInfo))),
    STDMETHOD(HRESULT, "GetTypeInfoType", c_int, POINTER(TYPEKIND)),
    STDMETHOD(HRESULT, "GetTypeInfoOfGuid", REFGUID, POINTER(POINTER(ITypeInfo))),
    STDMETHOD(HRESULT, "GetLibAttr", POINTER(POINTER(TLIBATTR))),
    STDMETHOD(HRESULT, "GetTypeComp", POINTER(ITypeComp)),
    STDMETHOD(HRESULT, "GetDocumentation", c_int, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ulong), POINTER(BSTR)),
    STDMETHOD(HRESULT, "IsName", c_wchar_p, c_ulong, c_int),
    STDMETHOD(HRESULT, "FindName", c_wchar_p, c_ulong, POINTER(POINTER(ITypeInfo)),
              POINTER(MEMBERID), POINTER(c_uint)),
    STDMETHOD(HRESULT, "ReleaseTLibAttr", POINTER(TLIBATTR))]

IDispatch._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "GetTypeInfoCount", POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetTypeInfo", c_uint, LCID, POINTER(POINTER(ITypeInfo))),
    STDMETHOD(HRESULT, "GetIDsOfNames", REFIID, POINTER(c_wchar_p), c_uint,
              LCID, POINTER(DISPID)),
    STDMETHOD(HRESULT, "Invoke", DISPID, REFIID, LCID, WORD, POINTER(DISPPARAMS),
              POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(c_uint))]

################################################################
# functions
#

def LoadTypeLib(fnm):
    p = pointer(ITypeLib())
    oleaut32.LoadTypeLib(unicode(fnm), byref(p))
    return p

def LoadTypeLibEx(fnm, regkind=REGKIND_NONE):
    p = pointer(ITypeLib())
    oleaut32.LoadTypeLibEx(unicode(fnm), regkind, byref(p))
    return p

def LoadRegTypeLib(rguid, wVerMajor, wVerMinor, lcid):
    p = pointer(ITypeLib())
    oleaut32.LoadRegTypeLib(rguid, wVerMajor, wVerMinor, lcid, byref(p))
    return p

################################################################
S_OK = 0

class DualObjImpl(COMObject):

    def __init__(self):
        COMObject.__init__(self)
        self.LoadTypeInfo()

    def LoadTypeInfo(self):
        interface = self._com_interfaces_[0]
        tlib = pointer(ITypeLib())
        oleaut32.LoadRegTypeLib(byref(self._typelib_.guid),
                                self._typelib_.version[0],
                                self._typelib_.version[1],
                                0,
                                byref(tlib))
        typeinfo = pointer(ITypeInfo())
        tlib.GetTypeInfoOfGuid(byref(interface._iid_), byref(typeinfo))
        self.typeinfo = typeinfo

    # IDispatch methods

    def GetIDsOfNames(self, this, riid, rgszNames, cNames, lcid, rgDispid):
        # We use windll.oleaut32 instead of oledll.oleaut32 because
        # we don't want an exception here, instead we pass the returned HRESULT
        # value to the caller.
        return windll.oleaut32.DispGetIDsOfNames(self.typeinfo, rgszNames,
                                                 cNames, rgDispid)

    def Invoke(self, this, dispid, refiid, lcid, wFlags,
               pDispParams, pVarResult, pExcepInfo, puArgErr):
        # See the comment in GetIDsOfNames
        return windll.oleaut32.DispInvoke(this, self.typeinfo, dispid,
                                          wFlags, pDispParams,
                                          pVarResult, pExcepInfo, puArgErr)

    def GetTypeInfoCount(self, this, pctInfo):
        if pctInfo:
            pctInfo[0] = 1
        return S_OK

    def GetTypeInfo(self, this, index, lcid, ppTInfo):
        # *ppTInfo = self.typeinfo
        from ctypes import addressof, c_voidp
        addr = c_voidp.from_address(addressof(ppTInfo)).value
        c_voidp.from_address(addr).value = addressof(self.typeinfo.contents)
        self.typeinfo.AddRef()
        return S_OK
