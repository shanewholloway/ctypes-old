from ctcom import IUnknown, COMPointer, GUID, LCID, REFIID, REFGUID, PPUNK, PUNK, WORD

from ctypes import Structure, Union, POINTER, byref, oledll, \
     c_short, c_ushort, c_int, c_uint, c_long, c_ulong, c_wchar_p, c_voidp

oleaut32 = oledll.oleaut32

################################################################
# Interfaces declarations
#
def _mth(*args):
    return args

# fake
from ctcom import IUnknownPointer
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

################################################################
# typeinfo, typelib and automation data types
#
DISPID = c_long
MEMBERID = DISPID
TYPEKIND = c_int # enum

class BSTR(Union):
    _fields_ = [("_ptr", "i"),
                ("value", "Z")]

    def __init__(self, text=None):
        if text is not None:
            self._ptr = oleaut32.SysAllocString(unicode(text))

    def from_param(cls, param):
        return cls(param)
    from_param = classmethod(from_param)

    def _as_parameter_(self):
        return self._ptr
    _as_parameter_ = property(_as_parameter_)

    def __repr__(self):
        if self._ptr:
            return "<BSTR '%s'>" % self.value
        else:
            return "<BSTR (NULL)>"

    def __del__(self, SysFreeString=oleaut32.SysFreeString):
        if self._ptr:
            SysFreeString(self._ptr)
# XXX BUG: Crashed hard when _ptr set to 0
##            self._ptr = 0

#fake it, in reality it's a union having 16 bytes
class VARIANT(Structure):
    class U(Union):
        _fields_ = [("bVal", "B"),
                    ("iVal", "h"),
                    ("lVal", "l"),
                    ("fltVal", "f"),
                    ("dblVal", "d"),
                    ("boolVal", "i"),
                    ("strVal", "Z"), # XXX ???
                    # ...
                    ("pUnkVal", IUnknownPointer),
                    ("pDispVal", IDispatchPointer),
                    ]

    _fields_ = [("vt", "H"),
                ("wReserved1", "H"),
                ("wReserved2", "H"),
                ("wReserved3", "H"),
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

class DISPPARAMS(Structure):
    _fields_ = [("rgvarg", POINTER(VARIANT)),
                ("rgdispidNamedArgs", POINTER(DISPID)),
                ("cArgs", "I"),
                ("cNamedArgs", "I")]

# c:/vc98/include/oaidl.h

class EXCEPINFO(Structure):
    _fields_ = [("wCode", "H"),
                ("wReserved", "H"),
                ("bstrSource", BSTR),
                ("bstrDescription", BSTR),
                ("bstrHelpFile", BSTR),
                ("dwHelpContext", "L"),
                ("pvReserved", "P"),
                ("pfnDeferredFillIn", "P"),
                ("scode", "L")]

class TLIBATTR(Structure):
    _fields_ = [("guid", GUID),
                ("lcid", "L"),
                ("syskind", "i"),
                ("wMajorVersionNum", "H"),
                ("wMinorVersionNum", "H"),
                ("wLibFlags", "H")]

class PARAMDESCEX(Structure):
    _fields_ = [("cBytes", "L"),
                ("varDefaultValue", VARIANT)]
    
class PARAMDESC(Structure):
    _fields_ = [("pPARAMDescEx", POINTER(PARAMDESCEX)),
                ("wPARAMFlags", "H")]

LPTYPEDESC = POINTER("TYPEDESC")

# VARTYPE is unsigned short!

class TYPEDESC(Structure):
    class U(Union):
        _fields_ = [("lptdesc", LPTYPEDESC),
##                    ("lpadesc", POINTER(ARRAYDESC)),
                    ("hreftype", "L")]    
    _fields_ = [("u", U),
                ("vt", "H")]

LPTYPEDESC.set_type(TYPEDESC)

class IDLDESC(Structure):
    _fields_ = [("dwReserved", "L"),
                ("wIDLFlags", "H")]

class TYPEATTR(Structure):
    _fields_ = [("guid", GUID),
                ("lcid", "i"),
                ("dwReserved", "L"),
                ("memidConstructor", "l"),
                ("memidDestructor", "l"),
                ("lpstrSchema", "Z"),
                ("cbSizeInstance", "L"),
                ("typekind", "i"),
                ("cFuncs", "H"),
                ("cVars", "H"),
                ("cImplTypes", "H"),
                ("cbSizeVft", "H"),
                ("cbAlignment", "H"),
                ("wTypeFlags", "H"),
                ("wMajorVerNum", "H"),
                ("wMinorVerNum", "H"),
                ("tdescAlias", TYPEDESC),
                ("idldescType", IDLDESC),
                ]
LPTYPEATTR = POINTER(TYPEATTR)

class ELEMDESC(Structure):
    _fields_ = [("tdesc", TYPEDESC),
                ("paramdesc", PARAMDESC)]
                
class VARDESC(Structure):
    class U(Union):
        _fields_ = [("oInst", "L"),
                    ("lpvarValue", POINTER(VARIANT))]
    _fields_ = [("memid", "I"),
                ("strSchema", "Z"),
                ("u", U),
                ("elemdescVar", ELEMDESC),
                ("wVarFlags", "H"),
                ("varkind", "I")]
LPVARDESC = POINTER(VARDESC)

class FUNCDESC(Structure):
    _fields_ = [("memid", "l"),
                ("lprgscode", "i"),
                ("lprgelemdescParam", POINTER(ELEMDESC)),
                ("funckind", "i"),
                ("invkind", "i"),
                ("callconv", "i"),
                ("cParams", "h"),
                ("cParamsOpt", "h"),
                ("oVft", "h"),
                ("cScodes", "h"),
                ("elemdescFunc", ELEMDESC),
                ("wFuncFlags", "H")]
LPFUNCDESC = POINTER(FUNCDESC)

################################################################
# The interfaces COM methods

ITypeInfo._methods_ = [("GetTypeAttr", (POINTER(LPTYPEATTR),)),
                       ("GetTypeComp", (POINTER(ITypeCompPointer),)),
                       ("GetFuncDesc", (c_uint,  POINTER(POINTER(FUNCDESC)))),
                       ("GetVarDesc", (c_uint, POINTER(POINTER(VARDESC)))),
                       ("GetNames", (MEMBERID, POINTER(BSTR), c_uint, POINTER(c_uint))),
                       ("GetRefTypeOfImplType", (c_uint, POINTER(HREFTYPE))),
                       ("GetImplTypeFlags", (c_uint, POINTER(c_int))),
                       ("GetIDsOfNames", (POINTER(LPOLESTR), c_uint, POINTER(c_int))),
                       ("Invoke", (PUNK, MEMBERID, WORD, POINTER(DISPPARAMS),
                                   POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(c_uint))),
                       ("GetDocumentation", (MEMBERID, POINTER(BSTR), POINTER(BSTR),
                                                 POINTER(c_ulong), POINTER(BSTR))),
                       ("GetDllEntry", (MEMBERID, c_int, POINTER(BSTR), POINTER(BSTR),
                                            POINTER(c_ushort))),
                       ("GetRefTypeInfo", (HREFTYPE, POINTER(ITypeInfoPointer))),
                       ("AddressOfMember", (MEMBERID, c_int, POINTER(c_voidp))),
                       ("CreateInstance", (c_voidp, REFIID, PPUNK)),
                       ("GetMops", (MEMBERID, POINTER(BSTR))),
                       ("GetContainingTypeLib", (POINTER(ITypeLibPointer), POINTER(c_uint))),
                       ("ReleaseTypeAttr", (LPTYPEATTR,)),
                       ("ReleaseFuncDesc", (LPFUNCDESC,)),
                       ("ReleaseVarDesc", (LPVARDESC,))]

ITypeLib._methods_ = [("GetTypeInfoCount", ()),
                      ("GetTypeInfo", (c_uint, POINTER(ITypeInfoPointer))),
                      ("GetTypeInfoType", (c_int, POINTER(TYPEKIND))),
                      ("GetTypeInfoOfGuid", (REFGUID, POINTER(ITypeInfoPointer))),
                      ("GetLibAttr", (POINTER(TLIBATTR),)),
                      ("GetTypeComp", (POINTER(ITypeComp),)),
                      ("GetDocumentation", (c_int, POINTER(BSTR), POINTER(BSTR),
                                                POINTER(c_ulong), POINTER(BSTR))),
                      ("IsName", (c_wchar_p, c_ulong, c_int)),
                      ("FindName", (c_wchar_p, c_ulong, POINTER(ITypeInfoPointer),
                                        POINTER(MEMBERID), POINTER(c_uint))),
                      ("ReleaseTLibAttr", (POINTER(TLIBATTR),))]

IDispatch._methods_ = [("GetTypeInfoCount", (POINTER(c_uint),)),
                       ("GetTypeInfo", (c_uint, LCID, POINTER(ITypeInfoPointer))),
                       ("GetIDsOfNames", (REFIID, POINTER(c_wchar_p), c_uint,
                                          LCID, POINTER(DISPID))),
                       ("Invoke", (DISPID, REFIID, LCID, WORD, POINTER(DISPPARAMS),
                                   POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(c_uint)))]

################################################################
# functions
#

def LoadTypeLib(fnm):
    p = ITypeLibPointer()
    oleaut32.LoadTypeLib(unicode(fnm), byref(p))
    return p

if __name__ == '__main__':
    path = r"c:\tss5\bin\debug\ITInfo.dll"
    p = LoadTypeLib(path)
