# generated by 'xml2py'
# flags 'windows.xml -s ITypeLib -s TYPEFLAGS'
# ... and patched by hand
from ctypes import *
from comtypes import IUnknown, GUID, BSTR, STDMETHOD

UINT = c_uint # typedef
LONG = c_long # typedef
INT = c_int # typedef
WCHAR = c_wchar # typedef
OLECHAR = WCHAR # typedef
DWORD = c_ulong # typedef
LPOLESTR = POINTER(OLECHAR) # typedef
BOOL = c_int # typedef
DISPID = LONG # typedef
MEMBERID = DISPID # typedef
USHORT = c_ushort # typedef
WORD = c_ushort # typedef
LCID = DWORD # typedef
HREFTYPE = DWORD # typedef
PVOID = c_void_p # typedef
SCODE = LONG # typedef
VARTYPE = c_ushort # typedef
ULONG_PTR = c_ulong # typedef
LONGLONG = c_longlong # typedef
BYTE = c_ubyte # typedef
SHORT = c_short # typedef
FLOAT = c_float # typedef
DOUBLE = c_double # typedef
VARIANT_BOOL = c_short # typedef
DATE = c_double # typedef
CHAR = c_char # typedef
ULONGLONG = c_ulonglong # typedef

################################################################

PARAMFLAG_NONE = 0
PARAMFLAG_FIN = 1
PARAMFLAG_FOUT = 2
PARAMFLAG_FLCID = 4
PARAMFLAG_FRETVAL = 8
PARAMFLAG_FOPT = 16
PARAMFLAG_FHASDEFAULT = 32
PARAMFLAG_FHASCUSTDATA = 64

IMPLTYPEFLAG_FDEFAULT = 1
IMPLTYPEFLAG_FSOURCE = 2
IMPLTYPEFLAG_FRESTRICTED = 4
IMPLTYPEFLAG_FDEFAULTVTABLE = 8

tagFUNCFLAGS = c_int # enum
FUNCFLAG_FRESTRICTED = 1
FUNCFLAG_FSOURCE = 2
FUNCFLAG_FBINDABLE = 4
FUNCFLAG_FREQUESTEDIT = 8
FUNCFLAG_FDISPLAYBIND = 16
FUNCFLAG_FDEFAULTBIND = 32
FUNCFLAG_FHIDDEN = 64
FUNCFLAG_FUSESGETLASTERROR = 128
FUNCFLAG_FDEFAULTCOLLELEM = 256
FUNCFLAG_FUIDEFAULT = 512
FUNCFLAG_FNONBROWSABLE = 1024
FUNCFLAG_FREPLACEABLE = 2048
FUNCFLAG_FIMMEDIATEBIND = 4096
FUNCFLAGS = tagFUNCFLAGS

DISPATCH_PROPERTYPUTREF = 8
DISPATCH_PROPERTYPUT = 4
DISPATCH_PROPERTYGET = 2
DISPATCH_METHOD = 1

tagVARFLAGS = c_int # enum
VARFLAG_FREADONLY = 1
VARFLAG_FSOURCE = 2
VARFLAG_FBINDABLE = 4
VARFLAG_FREQUESTEDIT = 8
VARFLAG_FDISPLAYBIND = 16
VARFLAG_FDEFAULTBIND = 32
VARFLAG_FHIDDEN = 64
VARFLAG_FRESTRICTED = 128
VARFLAG_FDEFAULTCOLLELEM = 256
VARFLAG_FUIDEFAULT = 512
VARFLAG_FNONBROWSABLE = 1024
VARFLAG_FREPLACEABLE = 2048
VARFLAG_FIMMEDIATEBIND = 4096
VARFLAGS = tagVARFLAGS

tagSYSKIND = c_int # enum
SYS_WIN16 = 0
SYS_WIN32 = 1
SYS_MAC = 2
SYS_WIN64 = 3
SYSKIND = tagSYSKIND # typedef

tagTYPEKIND = c_int # enum
TKIND_ENUM = 0
TKIND_RECORD = 1
TKIND_MODULE = 2
TKIND_INTERFACE = 3
TKIND_DISPATCH = 4
TKIND_COCLASS = 5
TKIND_ALIAS = 6
TKIND_UNION = 7
TKIND_MAX = 8
TYPEKIND = tagTYPEKIND # typedef

VARENUM = c_int # enum
VT_EMPTY = 0
VT_NULL = 1
VT_I2 = 2
VT_I4 = 3
VT_R4 = 4
VT_R8 = 5
VT_CY = 6
VT_DATE = 7
VT_BSTR = 8
VT_DISPATCH = 9
VT_ERROR = 10
VT_BOOL = 11
VT_VARIANT = 12
VT_UNKNOWN = 13
VT_DECIMAL = 14
VT_I1 = 16
VT_UI1 = 17
VT_UI2 = 18
VT_UI4 = 19
VT_I8 = 20
VT_UI8 = 21
VT_INT = 22
VT_UINT = 23
VT_VOID = 24
VT_HRESULT = 25
VT_PTR = 26
VT_SAFEARRAY = 27
VT_CARRAY = 28
VT_USERDEFINED = 29
VT_LPSTR = 30
VT_LPWSTR = 31
VT_RECORD = 36
VT_INT_PTR = 37
VT_UINT_PTR = 38
VT_FILETIME = 64
VT_BLOB = 65
VT_STREAM = 66
VT_STORAGE = 67
VT_STREAMED_OBJECT = 68
VT_STORED_OBJECT = 69
VT_BLOB_OBJECT = 70
VT_CF = 71
VT_CLSID = 72
VT_VERSIONED_STREAM = 73
VT_BSTR_BLOB = 4095
VT_VECTOR = 4096
VT_ARRAY = 8192
VT_BYREF = 16384
VT_RESERVED = 32768
VT_ILLEGAL = 65535
VT_ILLEGALMASKED = 4095
VT_TYPEMASK = 4095

tagTYPEFLAGS = c_int # enum
TYPEFLAG_FAPPOBJECT = 1
TYPEFLAG_FCANCREATE = 2
TYPEFLAG_FLICENSED = 4
TYPEFLAG_FPREDECLID = 8
TYPEFLAG_FHIDDEN = 16
TYPEFLAG_FCONTROL = 32
TYPEFLAG_FDUAL = 64
TYPEFLAG_FNONEXTENSIBLE = 128
TYPEFLAG_FOLEAUTOMATION = 256
TYPEFLAG_FRESTRICTED = 512
TYPEFLAG_FAGGREGATABLE = 1024
TYPEFLAG_FREPLACEABLE = 2048
TYPEFLAG_FDISPATCHABLE = 4096
TYPEFLAG_FREVERSEBIND = 8192
TYPEFLAG_FPROXY = 16384
TYPEFLAGS = tagTYPEFLAGS # typedef

tagDESCKIND = c_int # enum
DESCKIND_NONE = 0
DESCKIND_FUNCDESC = 1
DESCKIND_VARDESC = 2
DESCKIND_TYPECOMP = 3
DESCKIND_IMPLICITAPPOBJ = 4
DESCKIND_MAX = 5
DESCKIND = tagDESCKIND # typedef

tagINVOKEKIND = c_int # enum
INVOKE_FUNC = 1
INVOKE_PROPERTYGET = 2
INVOKE_PROPERTYPUT = 4
INVOKE_PROPERTYPUTREF = 8
INVOKEKIND = tagINVOKEKIND # typedef

tagVARKIND = c_int # enum
VAR_PERINSTANCE = 0 # enum tagVARKIND
VAR_STATIC = 1 # enum tagVARKIND
VAR_CONST = 2 # enum tagVARKIND
VAR_DISPATCH = 3 # enum tagVARKIND
VARKIND = tagVARKIND # typedef

tagFUNCKIND = c_int # enum
FUNC_VIRTUAL = 0
FUNC_PUREVIRTUAL = 1
FUNC_NONVIRTUAL = 2
FUNC_STATIC = 3
FUNC_DISPATCH = 4
FUNCKIND = tagFUNCKIND # typedef

tagCALLCONV = c_int # enum
CC_FASTCALL = 0
CC_CDECL = 1
CC_MSCPASCAL = 2
CC_PASCAL = 2
CC_MACPASCAL = 3
CC_STDCALL = 4
CC_FPFASTCALL = 5
CC_SYSCALL = 6
CC_MPWCDECL = 7
CC_MPWPASCAL = 8
CC_MAX = 9
CALLCONV = tagCALLCONV # typedef

tagREGKIND = c_int # enum
REGKIND_DEFAULT = 0
REGKIND_REGISTER = 1
REGKIND_NONE = 2
REGKIND = tagREGKIND # typedef

################################################################

class tagTLIBATTR(Structure):
    _fields_ = [
        ('guid', GUID),
        ('lcid', LCID),
        ('syskind', SYSKIND),
        ('wMajorVerNum', WORD),
        ('wMinorVerNum', WORD),
        ('wLibFlags', WORD),
    ]
assert sizeof(tagTLIBATTR) == 32, sizeof(tagTLIBATTR)
assert alignment(tagTLIBATTR) == 4, alignment(tagTLIBATTR)
TLIBATTR = tagTLIBATTR # typedef

class tagIDLDESC(Structure):
    _fields_ = [
        ('dwReserved', ULONG_PTR),
        ('wIDLFlags', USHORT),
    ]
assert sizeof(tagIDLDESC) == 8, sizeof(tagIDLDESC)
assert alignment(tagIDLDESC) == 4, alignment(tagIDLDESC)
IDLDESC = tagIDLDESC # typedef

class tagSAFEARRAYBOUND(Structure):
    _fields_ = [
        ('cElements', DWORD),
        ('lLbound', LONG),
    ]
assert sizeof(tagSAFEARRAYBOUND) == 8, sizeof(tagSAFEARRAYBOUND)
assert alignment(tagSAFEARRAYBOUND) == 4, alignment(tagSAFEARRAYBOUND)
SAFEARRAYBOUND = tagSAFEARRAYBOUND # typedef

class tagSAFEARRAY(Structure):
    _fields_ = [
        ('cDims', USHORT),
        ('fFeatures', USHORT),
        ('cbElements', DWORD),
        ('cLocks', DWORD),
        ('pvData', PVOID),
        ('rgsabound', SAFEARRAYBOUND * 1),
    ]
assert sizeof(tagSAFEARRAY) == 24, sizeof(tagSAFEARRAY)
assert alignment(tagSAFEARRAY) == 4, alignment(tagSAFEARRAY)
SAFEARRAY = tagSAFEARRAY # typedef

class tagEXCEPINFO(Structure):
    pass
tagEXCEPINFO._fields_ = [
    ('wCode', WORD),
    ('wReserved', WORD),
    ('bstrSource', BSTR),
    ('bstrDescription', BSTR),
    ('bstrHelpFile', BSTR),
    ('dwHelpContext', DWORD),
    ('pvReserved', PVOID),
    ('pfnDeferredFillIn', WINFUNCTYPE(HRESULT, POINTER(tagEXCEPINFO))),
    ('scode', SCODE),
]
assert sizeof(tagEXCEPINFO) == 32, sizeof(tagEXCEPINFO)
assert alignment(tagEXCEPINFO) == 4, alignment(tagEXCEPINFO)
EXCEPINFO = tagEXCEPINFO # typedef

################################################################

class ITypeLib(IUnknown):
    # c:/vc98/include/OAIDL.H 4460
    _iid_ = GUID("{00020402-0000-0000-C000-000000000046}")

##    STDMETHOD(UINT, 'GetTypeInfoCount', []),
##    def GetTypeInfoCount(self):
##        "Return the number of typeinfos in this library"
##        return self.__com_GetTypeInfoCount()

##    STDMETHOD(HRESULT, 'GetTypeInfo', [UINT, POINTER(POINTER(ITypeInfo))]),
    def GetTypeInfo(self, index):
        "Return typeinfo for index"
        p = POINTER(ITypeInfo)()
        self.__com_GetTypeInfo(index, byref(p))
        return p

##    STDMETHOD(HRESULT, 'GetTypeInfoType', [UINT, POINTER(TYPEKIND)]),
    def GetTypeInfoType(self, index):
        "Return the TYPEKIND for this typeinfo"
        p = TYPEKIND()
        self.__com_GetTypeInfoType(index, byref(p))
        return p.value

##    STDMETHOD(HRESULT, 'GetTypeInfoOfGuid', [POINTER(GUID), POINTER(POINTER(ITypeInfo))]),
    def GetTypeInfoOfGuid(self, p0, p1):
        pass

##    STDMETHOD(HRESULT, 'GetLibAttr', [POINTER(POINTER(TLIBATTR))]),
    def GetLibAttr(self):
        p = POINTER(TLIBATTR)()
        self.__com_GetLibAttr(byref(p))
        # XXX register for release
        return p

##    STDMETHOD(HRESULT, 'GetTypeComp', [POINTER(POINTER(ITypeComp))]),
    def GetTypeComp(self, p0):
        pass

##    STDMETHOD(HRESULT, 'GetDocumentation', [INT, POINTER(BSTR), POINTER(BSTR), POINTER(DWORD), POINTER(BSTR)]),
    def GetDocumentation(self, index):
        " Return the name, documentation, helpcontext, and helpfile for this typeinfo"
        name = BSTR()
        doc = BSTR()
        helpcontext = DWORD()
        helpfile = BSTR()
        self.__com_GetDocumentation(index, byref(name), byref(doc),
                                    byref(helpcontext), byref(helpfile))
        return name.value, doc.value, helpcontext.value, helpfile.value

##    STDMETHOD(HRESULT, 'IsName', [LPOLESTR, DWORD, POINTER(BOOL)]),
    def IsName(self, p0, p1, p2):
        pass

##    STDMETHOD(HRESULT, 'FindName', [LPOLESTR, DWORD, POINTER(POINTER(ITypeInfo)), POINTER(MEMBERID), POINTER(USHORT)]),
    def FindName(self, p0, p1, p2, p3, p4):
        pass

##    STDMETHOD(None, 'ReleaseTLibAttr', [POINTER(TLIBATTR)]),
    def ReleaseTLibAttr(self, p0):
        pass

class ITypeInfo(IUnknown):
    def GetTypeAttr(self):
        p = POINTER(TYPEATTR)()
        self.__com_GetTypeAttr(byref(p))
        result = p[0]
        result._owner = (self, p)
        return result

    def GetTypeComp(self, p0):
        pass

    def GetFuncDesc(self, index):
        p = POINTER(FUNCDESC)()
        self.__com_GetFuncDesc(index, byref(p))
        # XXX release
        return p[0]

    def GetVarDesc(self, index):
        pvd = POINTER(VARDESC)()
        self.__com_GetVarDesc(index, byref(pvd))
        return pvd[0]

    def GetNames(self, memid, count):
        rgNames = (BSTR * count)()
        cNames = c_uint()
        self.__com_GetNames(memid, rgNames, count, byref(cNames))
        return rgNames[:cNames.value]

    def GetRefTypeOfImplType(self, index):
        "Return the reftype for a base interface"
        hreftype = HREFTYPE()
        self.__com_GetRefTypeOfImplType(index, byref(hreftype))
        return hreftype.value

    def GetImplTypeFlags(self, index):
        "Return the impltypeflags"
        flags = c_int()
        self.__com_GetImplTypeFlags(index, byref(flags))
        return flags.value

    def GetIDsOfNames(self, p0, p1, p2):
        pass

    def Invoke(self, p0, p1, p2, p3, p4, p5, p6):
        pass

    def GetDocumentation(self, memberid):
        " Return the name, documentation, helpcontext, and helpfile for this typeinfo"
        name = BSTR()
        doc = BSTR()
        helpcontext = DWORD()
        helpfile = BSTR()
        self.__com_GetDocumentation(memberid, byref(name), byref(doc),
                                    byref(helpcontext), byref(helpfile))
        return name.value, doc.value, helpcontext.value, helpfile.value

    def GetDllEntry(self, memid, invkind):
        "Return the dll name, function name, and ordinal for a function and invkind."
        dllname = BSTR()
        name = BSTR()
        ordinal = c_ushort()
        self.__com_GetDllEntry(memid, invkind, byref(dllname), byref(name), byref(ordinal))
        return dllname.value, name.value, ordinal.value

    def GetRefTypeInfo(self, hreftype):
        "Return a referenced typeinfo"
        p = POINTER(ITypeInfo)()
        self.__com_GetRefTypeInfo(hreftype, byref(p))
        return p

    def AddressOfMember(self, p0, p1, p2):
        pass

    def CreateInstance(self, p0, p1, p2):
        pass

    def GetMops(self, p0, p1):
        pass

    def GetContainingTypeLib(self, p0, p1):
        pass

    def ReleaseTypeAttr(self, pta):
        self.__com_ReleaseTypeAttr(pta)

    def ReleaseFuncDesc(self, p0):
        pass

    def ReleaseVarDesc(self, p0):
        pass


class ITypeComp(IUnknown):
    def Bind(self, p0, p1, p2, p3, p4, p5):
        pass

    def BindType(self, p0, p1, p2, p3):
        pass

ITypeLib._methods_ = [
    STDMETHOD(UINT, 'GetTypeInfoCount', []),
    STDMETHOD(HRESULT, 'GetTypeInfo', [UINT, POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(HRESULT, 'GetTypeInfoType', [UINT, POINTER(TYPEKIND)]),
    STDMETHOD(HRESULT, 'GetTypeInfoOfGuid', [POINTER(GUID), POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(HRESULT, 'GetLibAttr', [POINTER(POINTER(TLIBATTR))]),
    STDMETHOD(HRESULT, 'GetTypeComp', [POINTER(POINTER(ITypeComp))]),
    STDMETHOD(HRESULT, 'GetDocumentation', [INT, POINTER(BSTR), POINTER(BSTR), POINTER(DWORD), POINTER(BSTR)]),
    STDMETHOD(HRESULT, 'IsName', [LPOLESTR, DWORD, POINTER(BOOL)]),
    STDMETHOD(HRESULT, 'FindName', [LPOLESTR, DWORD, POINTER(POINTER(ITypeInfo)), POINTER(MEMBERID), POINTER(USHORT)]),
    STDMETHOD(None, 'ReleaseTLibAttr', [POINTER(TLIBATTR)]),
]
IID = GUID # typedef

class tagBINDPTR(Union):
    pass
BINDPTR = tagBINDPTR # typedef
ITypeComp._methods_ = [
    STDMETHOD(HRESULT, 'Bind', [LPOLESTR, DWORD, WORD, POINTER(POINTER(ITypeInfo)), POINTER(DESCKIND), POINTER(BINDPTR)]),
    STDMETHOD(HRESULT, 'BindType', [LPOLESTR, DWORD, POINTER(POINTER(ITypeInfo)), POINTER(POINTER(ITypeComp))]),
]

class tagTYPEATTR(Structure):
    _owner = None
    def __del__(self):
        if self._owner:
            self._owner[0].ReleaseTypeAttr(self._owner[1])
TYPEATTR = tagTYPEATTR # typedef
class tagFUNCDESC(Structure):
    pass
FUNCDESC = tagFUNCDESC # typedef
class tagVARDESC(Structure):
    pass
VARDESC = tagVARDESC # typedef
class tagDISPPARAMS(Structure):
    pass
DISPPARAMS = tagDISPPARAMS # typedef
class tagVARIANT(Structure):
    pass
VARIANT = tagVARIANT # typedef

def from_param(self, var):
    # XXX
    # InternetExplorer sometimes(?) requires POINTER(VARIANT)
    # as [in] parameters, in the Navigate2 call.  But the method gets
    # a simple string value.
    #
    # We could use from_param to accept simple values, convert them to VARIANT,
    # and finally pass a byref() to that to the function call.
    if isinstance(var, POINTER(VARIANT)):
        return var
    if isinstance(var, VARIANT):
        return byref(var)
    elif isinstance(var, basestring):
        v = VARIANT()
        v.n1.n2.vt = VT_BSTR
        v.n1.n2.n3.bstrVal = var
        return byref(v)
    elif isinstance(var, (int, long)):
        v = VARIANT()
        v.n1.n2.vt = VT_I4
        v.n1.n2.n3.iVal = var
        return byref(v)
    raise TypeError, var

POINTER(VARIANT).from_param = classmethod(from_param)


ITypeInfo._methods_ = [
    STDMETHOD(HRESULT, 'GetTypeAttr', [POINTER(POINTER(TYPEATTR))]),
    STDMETHOD(HRESULT, 'GetTypeComp', [POINTER(POINTER(ITypeComp))]),
    STDMETHOD(HRESULT, 'GetFuncDesc', [UINT, POINTER(POINTER(FUNCDESC))]),
    STDMETHOD(HRESULT, 'GetVarDesc', [UINT, POINTER(POINTER(VARDESC))]),
    STDMETHOD(HRESULT, 'GetNames', [MEMBERID, POINTER(BSTR), UINT, POINTER(UINT)]),
    STDMETHOD(HRESULT, 'GetRefTypeOfImplType', [UINT, POINTER(HREFTYPE)]),
    STDMETHOD(HRESULT, 'GetImplTypeFlags', [UINT, POINTER(INT)]),
    STDMETHOD(HRESULT, 'GetIDsOfNames', [POINTER(LPOLESTR), UINT, POINTER(MEMBERID)]),
    STDMETHOD(HRESULT, 'Invoke', [PVOID, MEMBERID, WORD, POINTER(DISPPARAMS), POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(UINT)]),
    STDMETHOD(HRESULT, 'GetDocumentation', [MEMBERID, POINTER(BSTR), POINTER(BSTR), POINTER(DWORD), POINTER(BSTR)]),
    STDMETHOD(HRESULT, 'GetDllEntry', [MEMBERID, INVOKEKIND, POINTER(BSTR), POINTER(BSTR), POINTER(WORD)]),
    STDMETHOD(HRESULT, 'GetRefTypeInfo', [HREFTYPE, POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(HRESULT, 'AddressOfMember', [MEMBERID, INVOKEKIND, POINTER(PVOID)]),
    STDMETHOD(HRESULT, 'CreateInstance', [POINTER(IUnknown), POINTER(IID), POINTER(PVOID)]),
    STDMETHOD(HRESULT, 'GetMops', [MEMBERID, POINTER(BSTR)]),
    STDMETHOD(HRESULT, 'GetContainingTypeLib', [POINTER(POINTER(ITypeLib)), POINTER(UINT)]),
    STDMETHOD(None, 'ReleaseTypeAttr', [POINTER(TYPEATTR)]),
    STDMETHOD(None, 'ReleaseFuncDesc', [POINTER(FUNCDESC)]),
    STDMETHOD(None, 'ReleaseVarDesc', [POINTER(VARDESC)]),
]

VARIANTARG = VARIANT # typedef
# tagDISPPARAMS
tagDISPPARAMS._fields_ = [
    ('rgvarg', POINTER(VARIANTARG)),
    ('rgdispidNamedArgs', POINTER(DISPID)),
    ('cArgs', UINT),
    ('cNamedArgs', UINT),
]
assert sizeof(tagDISPPARAMS) == 16, sizeof(tagDISPPARAMS)
assert alignment(tagDISPPARAMS) == 4, alignment(tagDISPPARAMS)
# tagBINDPTR
tagBINDPTR._fields_ = [
    ('lpfuncdesc', POINTER(FUNCDESC)),
    ('lpvardesc', POINTER(VARDESC)),
    ('lptcomp', POINTER(ITypeComp)),
]
assert sizeof(tagBINDPTR) == 4, sizeof(tagBINDPTR)
assert alignment(tagBINDPTR) == 4, alignment(tagBINDPTR)
class tagTYPEDESC(Structure):
    pass
class tagARRAYDESC(Structure):
    pass
# _py_N11tagTYPEDESC5__203E
class _py_N11tagTYPEDESC5__203E(Union):
    _fields_ = [
        ('lptdesc', POINTER(tagTYPEDESC)),
        ('lpadesc', POINTER(tagARRAYDESC)),
        ('hreftype', HREFTYPE),
]
assert sizeof(_py_N11tagTYPEDESC5__203E) == 4, sizeof(_py_N11tagTYPEDESC5__203E)
assert alignment(_py_N11tagTYPEDESC5__203E) == 4, alignment(_py_N11tagTYPEDESC5__203E)
# tagTYPEDESC
tagTYPEDESC._fields_ = [
    # Unnamed field renamed to '_'
    ('_', _py_N11tagTYPEDESC5__203E),
    ('vt', VARTYPE),
]
assert sizeof(tagTYPEDESC) == 8, sizeof(tagTYPEDESC)
assert alignment(tagTYPEDESC) == 4, alignment(tagTYPEDESC)
TYPEDESC = tagTYPEDESC # typedef

tagTYPEATTR._fields_ = [
    ('guid', GUID),
    ('lcid', LCID),
    ('dwReserved', DWORD),
    ('memidConstructor', MEMBERID),
    ('memidDestructor', MEMBERID),
    ('lpstrSchema', LPOLESTR),
    ('cbSizeInstance', DWORD),
    ('typekind', TYPEKIND),
    ('cFuncs', WORD),
    ('cVars', WORD),
    ('cImplTypes', WORD),
    ('cbSizeVft', WORD),
    ('cbAlignment', WORD),
    ('wTypeFlags', WORD),
    ('wMajorVerNum', WORD),
    ('wMinorVerNum', WORD),
    ('tdescAlias', TYPEDESC),
    ('idldescType', IDLDESC),
]
assert sizeof(tagTYPEATTR) == 76, sizeof(tagTYPEATTR)
assert alignment(tagTYPEATTR) == 4, alignment(tagTYPEATTR)
class _py_N10tagVARIANT5__200E(Union):
    pass
class __tagVARIANT(Structure):
    pass
class _py_N10tagVARIANT5__20012__tagVARIANT5__201E(Union):
    pass
class tagCY(Union):
    pass
class _py_N5tagCY5__143E(Structure):
    pass
# _py_N5tagCY5__143E
_py_N5tagCY5__143E._fields_ = [
    ('Lo', c_ulong),
    ('Hi', c_long),
]
assert sizeof(_py_N5tagCY5__143E) == 8, sizeof(_py_N5tagCY5__143E)
assert alignment(_py_N5tagCY5__143E) == 4, alignment(_py_N5tagCY5__143E)
# tagCY
tagCY._fields_ = [
    # Unnamed field renamed to '_'
    ('_', _py_N5tagCY5__143E),
    ('int64', LONGLONG),
]
assert sizeof(tagCY) == 8, sizeof(tagCY)
assert alignment(tagCY) == 8, alignment(tagCY)
CY = tagCY # typedef
class IDispatch(IUnknown):
    def GetTypeInfoCount(self, p0):
        pass

    def GetTypeInfo(self, p0, p1, p2):
        pass

    def GetIDsOfNames(self, p0, p1, p2, p3, p4):
        pass

    def Invoke(self, p0, p1, p2, p3, p4, p5, p6, p7):
        pass

class tagDEC(Structure):
    pass
DECIMAL = tagDEC # typedef
class __tagBRECORD(Structure):
    pass
class IRecordInfo(IUnknown):
    def RecordInit(self, p0):
        pass

    def RecordClear(self, p0):
        pass

    def RecordCopy(self, p0, p1):
        pass

    def GetGuid(self, p0):
        pass

    def GetName(self, p0):
        pass

    def GetSize(self, p0):
        pass

    def GetTypeInfo(self, p0):
        pass

    def GetField(self, p0, p1, p2):
        pass

    def GetFieldNoCopy(self, p0, p1, p2, p3):
        pass

    def PutField(self, p0, p1, p2, p3):
        pass

    def PutFieldNoCopy(self, p0, p1, p2, p3):
        pass

    def GetFieldNames(self, p0, p1):
        pass

    def IsMatchingType(self, p0):
        pass

    def RecordCreate(self):
        pass

    def RecordCreateCopy(self, p0, p1):
        pass

    def RecordDestroy(self, p0):
        pass

# __tagBRECORD
__tagBRECORD._fields_ = [
    ('pvRecord', PVOID),
    ('pRecInfo', POINTER(IRecordInfo)),
]
assert sizeof(__tagBRECORD) == 8, sizeof(__tagBRECORD)
assert alignment(__tagBRECORD) == 4, alignment(__tagBRECORD)
# _py_N10tagVARIANT5__20012__tagVARIANT5__201E
_py_N10tagVARIANT5__20012__tagVARIANT5__201E._fields_ = [
    ('llVal', LONGLONG),
    ('lVal', LONG),
    ('bVal', BYTE),
    ('iVal', SHORT),
    ('fltVal', FLOAT),
    ('dblVal', DOUBLE),
    ('boolVal', VARIANT_BOOL),
    ('scode', SCODE),
    ('cyVal', CY),
    ('date', DATE),
    ('bstrVal', BSTR),
    ('punkVal', POINTER(IUnknown)),
    ('pdispVal', POINTER(IDispatch)),
    ('parray', POINTER(SAFEARRAY)),
    ('pbVal', POINTER(BYTE)),
    ('piVal', POINTER(SHORT)),
    ('plVal', POINTER(LONG)),
    ('pllVal', POINTER(LONGLONG)),
    ('pfltVal', POINTER(FLOAT)),
    ('pdblVal', POINTER(DOUBLE)),
    ('pboolVal', POINTER(VARIANT_BOOL)),
    ('pscode', POINTER(SCODE)),
    ('pcyVal', POINTER(CY)),
    ('pdate', POINTER(DATE)),
    ('pbstrVal', POINTER(BSTR)),
    ('ppunkVal', POINTER(POINTER(IUnknown))),
    ('ppdispVal', POINTER(POINTER(IDispatch))),
    ('pparray', POINTER(POINTER(SAFEARRAY))),
    ('pvarVal', POINTER(VARIANT)),
    ('byref', PVOID),
    ('cVal', CHAR),
    ('uiVal', USHORT),
    ('ulVal', DWORD),
    ('ullVal', ULONGLONG),
    ('intVal', INT),
    ('uintVal', UINT),
    ('pdecVal', POINTER(DECIMAL)),
    ('pcVal', POINTER(CHAR)),
    ('puiVal', POINTER(USHORT)),
    ('pulVal', POINTER(DWORD)),
    ('pullVal', POINTER(ULONGLONG)),
    ('pintVal', POINTER(INT)),
    ('puintVal', POINTER(UINT)),
    ('brecVal', __tagBRECORD),
]
assert sizeof(_py_N10tagVARIANT5__20012__tagVARIANT5__201E) == 8, sizeof(_py_N10tagVARIANT5__20012__tagVARIANT5__201E)
assert alignment(_py_N10tagVARIANT5__20012__tagVARIANT5__201E) == 8, alignment(_py_N10tagVARIANT5__20012__tagVARIANT5__201E)
# __tagVARIANT
__tagVARIANT._fields_ = [
    ('vt', VARTYPE),
    ('wReserved1', WORD),
    ('wReserved2', WORD),
    ('wReserved3', WORD),
    ('n3', _py_N10tagVARIANT5__20012__tagVARIANT5__201E),
]
assert sizeof(__tagVARIANT) == 16, sizeof(__tagVARIANT)
assert alignment(__tagVARIANT) == 8, alignment(__tagVARIANT)
class _py_N6tagDEC5__144E(Union):
    pass
class _py_N6tagDEC5__1445__145E(Structure):
    pass
# _py_N6tagDEC5__1445__145E
_py_N6tagDEC5__1445__145E._fields_ = [
    ('scale', BYTE),
    ('sign', BYTE),
]
assert sizeof(_py_N6tagDEC5__1445__145E) == 2, sizeof(_py_N6tagDEC5__1445__145E)
assert alignment(_py_N6tagDEC5__1445__145E) == 1, alignment(_py_N6tagDEC5__1445__145E)
# _py_N6tagDEC5__144E
_py_N6tagDEC5__144E._fields_ = [
    # Unnamed field renamed to '_'
    ('_', _py_N6tagDEC5__1445__145E),
    ('signscale', USHORT),
]
assert sizeof(_py_N6tagDEC5__144E) == 2, sizeof(_py_N6tagDEC5__144E)
assert alignment(_py_N6tagDEC5__144E) == 2, alignment(_py_N6tagDEC5__144E)
class _py_N6tagDEC5__146E(Union):
    pass
class _py_N6tagDEC5__1465__147E(Structure):
    pass
# _py_N6tagDEC5__1465__147E
_py_N6tagDEC5__1465__147E._fields_ = [
    ('Lo32', DWORD),
    ('Mid32', DWORD),
]
assert sizeof(_py_N6tagDEC5__1465__147E) == 8, sizeof(_py_N6tagDEC5__1465__147E)
assert alignment(_py_N6tagDEC5__1465__147E) == 4, alignment(_py_N6tagDEC5__1465__147E)
# _py_N6tagDEC5__146E
_py_N6tagDEC5__146E._fields_ = [
    # Unnamed field renamed to '_'
    ('_', _py_N6tagDEC5__1465__147E),
    ('Lo64', ULONGLONG),
]
assert sizeof(_py_N6tagDEC5__146E) == 8, sizeof(_py_N6tagDEC5__146E)
assert alignment(_py_N6tagDEC5__146E) == 8, alignment(_py_N6tagDEC5__146E)
# tagDEC
tagDEC._fields_ = [
    ('wReserved', USHORT),
    # Unnamed field renamed to '_'
    ('_', _py_N6tagDEC5__144E),
    ('Hi32', DWORD),
    # Unnamed field renamed to '_1'
    ('_1', _py_N6tagDEC5__146E),
]
assert sizeof(tagDEC) == 16, sizeof(tagDEC)
assert alignment(tagDEC) == 8, alignment(tagDEC)
# _py_N10tagVARIANT5__200E
_py_N10tagVARIANT5__200E._fields_ = [
    ('n2', __tagVARIANT),
    ('decVal', DECIMAL),
]
assert sizeof(_py_N10tagVARIANT5__200E) == 16, sizeof(_py_N10tagVARIANT5__200E)
assert alignment(_py_N10tagVARIANT5__200E) == 8, alignment(_py_N10tagVARIANT5__200E)

# tagVARIANT
tagVARIANT._fields_ = [
    ('n1', _py_N10tagVARIANT5__200E),
]
assert sizeof(tagVARIANT) == 16, sizeof(tagVARIANT)
assert alignment(tagVARIANT) == 8, alignment(tagVARIANT)

class _py_N10tagVARDESC5__205E(Union):
    _fields_ = [
        ('oInst', DWORD),
        ('lpvarValue', POINTER(VARIANT)),
    ]
assert sizeof(_py_N10tagVARDESC5__205E) == 4, sizeof(_py_N10tagVARDESC5__205E)
assert alignment(_py_N10tagVARDESC5__205E) == 4, alignment(_py_N10tagVARDESC5__205E)

class tagELEMDESC(Structure):
    pass
class _py_N11tagELEMDESC5__204E(Union):
    pass
class tagPARAMDESC(Structure):
    pass
class tagPARAMDESCEX(Structure):
    pass
LPPARAMDESCEX = POINTER(tagPARAMDESCEX) # typedef
# tagPARAMDESC
tagPARAMDESC._fields_ = [
    ('pparamdescex', LPPARAMDESCEX),
    ('wParamFlags', USHORT),
]
assert sizeof(tagPARAMDESC) == 8, sizeof(tagPARAMDESC)
assert alignment(tagPARAMDESC) == 4, alignment(tagPARAMDESC)
PARAMDESC = tagPARAMDESC # typedef
# _py_N11tagELEMDESC5__204E
_py_N11tagELEMDESC5__204E._fields_ = [
    ('idldesc', IDLDESC),
    ('paramdesc', PARAMDESC),
]
assert sizeof(_py_N11tagELEMDESC5__204E) == 8, sizeof(_py_N11tagELEMDESC5__204E)
assert alignment(_py_N11tagELEMDESC5__204E) == 4, alignment(_py_N11tagELEMDESC5__204E)
# tagELEMDESC
tagELEMDESC._fields_ = [
    ('tdesc', TYPEDESC),
    # Unnamed field renamed to '_'
    ('_', _py_N11tagELEMDESC5__204E),
]
assert sizeof(tagELEMDESC) == 16, sizeof(tagELEMDESC)
assert alignment(tagELEMDESC) == 4, alignment(tagELEMDESC)
ELEMDESC = tagELEMDESC # typedef

# tagVARDESC
tagVARDESC._fields_ = [
    ('memid', MEMBERID),
    ('lpstrSchema', LPOLESTR),
    # Unnamed field renamed to '_'
    ('_', _py_N10tagVARDESC5__205E),
    ('elemdescVar', ELEMDESC),
    ('wVarFlags', WORD),
    ('varkind', VARKIND),
]
assert sizeof(tagVARDESC) == 36, sizeof(tagVARDESC)
assert alignment(tagVARDESC) == 4, alignment(tagVARDESC)

# tagFUNCDESC
tagFUNCDESC._fields_ = [
    ('memid', MEMBERID),
    ('lprgscode', POINTER(SCODE)),
    ('lprgelemdescParam', POINTER(ELEMDESC)),
    ('funckind', FUNCKIND),
    ('invkind', INVOKEKIND),
    ('callconv', CALLCONV),
    ('cParams', SHORT),
    ('cParamsOpt', SHORT),
    ('oVft', SHORT),
    ('cScodes', SHORT),
    ('elemdescFunc', ELEMDESC),
    ('wFuncFlags', WORD),
]
assert sizeof(tagFUNCDESC) == 52, sizeof(tagFUNCDESC)
assert alignment(tagFUNCDESC) == 4, alignment(tagFUNCDESC)

# tagPARAMDESCEX
tagPARAMDESCEX._fields_ = [
    ('cBytes', DWORD),
    ('varDefaultValue', VARIANTARG),
]
assert sizeof(tagPARAMDESCEX) == 24, sizeof(tagPARAMDESCEX)
assert alignment(tagPARAMDESCEX) == 8, alignment(tagPARAMDESCEX)
# tagARRAYDESC
tagARRAYDESC._fields_ = [
    ('tdescElem', TYPEDESC),
    ('cDims', USHORT),
    ('rgbounds', SAFEARRAYBOUND * 1),
]
assert sizeof(tagARRAYDESC) == 20, sizeof(tagARRAYDESC)
assert alignment(tagARRAYDESC) == 4, alignment(tagARRAYDESC)
LPCOLESTR = POINTER(OLECHAR) # typedef
IRecordInfo._methods_ = [
    STDMETHOD(HRESULT, 'RecordInit', [PVOID]),
    STDMETHOD(HRESULT, 'RecordClear', [PVOID]),
    STDMETHOD(HRESULT, 'RecordCopy', [PVOID, PVOID]),
    STDMETHOD(HRESULT, 'GetGuid', [POINTER(GUID)]),
    STDMETHOD(HRESULT, 'GetName', [POINTER(BSTR)]),
    STDMETHOD(HRESULT, 'GetSize', [POINTER(DWORD)]),
    STDMETHOD(HRESULT, 'GetTypeInfo', [POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(HRESULT, 'GetField', [PVOID, LPCOLESTR, POINTER(VARIANT)]),
    STDMETHOD(HRESULT, 'GetFieldNoCopy', [PVOID, LPCOLESTR, POINTER(VARIANT), POINTER(PVOID)]),
    STDMETHOD(HRESULT, 'PutField', [DWORD, PVOID, LPCOLESTR, POINTER(VARIANT)]),
    STDMETHOD(HRESULT, 'PutFieldNoCopy', [DWORD, PVOID, LPCOLESTR, POINTER(VARIANT)]),
    STDMETHOD(HRESULT, 'GetFieldNames', [POINTER(DWORD), POINTER(BSTR)]),
    STDMETHOD(BOOL, 'IsMatchingType', [POINTER(IRecordInfo)]),
    STDMETHOD(PVOID, 'RecordCreate', []),
    STDMETHOD(HRESULT, 'RecordCreateCopy', [PVOID, POINTER(PVOID)]),
    STDMETHOD(HRESULT, 'RecordDestroy', [PVOID]),
]
IDispatch._methods_ = [
    STDMETHOD(HRESULT, 'GetTypeInfoCount', [POINTER(UINT)]),
    STDMETHOD(HRESULT, 'GetTypeInfo', [UINT, LCID, POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(HRESULT, 'GetIDsOfNames', [POINTER(IID), POINTER(LPOLESTR), UINT, LCID, POINTER(DISPID)]),
    STDMETHOD(HRESULT, 'Invoke', [DISPID, POINTER(IID), LCID, WORD, POINTER(DISPPARAMS), POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(UINT)]),
]

################################################################

from ctypes.decorators import stdcall
@ stdcall(HRESULT, "oleaut32",
          [c_wchar_p, POINTER(POINTER(ITypeLib))])
def LoadTypeLib(name):
    p = POINTER(ITypeLib)()
    LoadTypeLib._api_(name, byref(p))
    return p

@ stdcall(HRESULT, "oleaut32",
          [c_wchar_p, REGKIND, POINTER(POINTER(ITypeLib))])
def LoadTypeLibEx(name, regkind=REGKIND_NONE):
    p = POINTER(ITypeLib)()
    LoadTypeLibEx._api_(name, regkind, byref(p))
    return p

##if __name__ == "__main__":
##    import ctypes
##    print ctypes.__file__
##    p = LoadTypeLibEx("aaa.bbb")
##    print p.AddRef()
