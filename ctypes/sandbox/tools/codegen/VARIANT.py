# todo: DECIMAL and CY need cleanup.
#
# generated by 'xml2py'
# flags 'windows.xml -s VARIANT -s ARRAYDESC -o VARIANT.py'
#
# Then, in one or two hours cleaned up to be human readable (somewhat)
from ctypes import *
from comtypes import GUID, IUnknown, STDMETHOD


################################################################
# types

HREFTYPE = c_ulong
VARTYPE = c_ushort
VARIANT_BOOL = c_short
SCODE = c_long
DATE = c_double
LCID = c_ulong
DISPID = c_long
MEMBERID = c_long

# enums

tagINVOKEKIND = c_int
INVOKE_FUNC = 1
INVOKE_PROPERTYGET = 2
INVOKE_PROPERTYPUT = 4
INVOKE_PROPERTYPUTREF = 8
INVOKEKIND = tagINVOKEKIND

tagSYSKIND = c_int
SYS_WIN16 = 0
SYS_WIN32 = 1
SYS_MAC = 2
SYS_WIN64 = 3
SYSKIND = tagSYSKIND

tagTYPEKIND = c_int
TKIND_ENUM = 0
TKIND_RECORD = 1
TKIND_MODULE = 2
TKIND_INTERFACE = 3
TKIND_DISPATCH = 4
TKIND_COCLASS = 5
TKIND_ALIAS = 6
TKIND_UNION = 7
TKIND_MAX = 8
TYPEKIND = tagTYPEKIND

tagDESCKIND = c_int
DESCKIND_NONE = 0
DESCKIND_FUNCDESC = 1
DESCKIND_VARDESC = 2
DESCKIND_TYPECOMP = 3
DESCKIND_IMPLICITAPPOBJ = 4
DESCKIND_MAX = 5
DESCKIND = tagDESCKIND

tagFUNCKIND = c_int
FUNC_VIRTUAL = 0
FUNC_PUREVIRTUAL = 1
FUNC_NONVIRTUAL = 2
FUNC_STATIC = 3
FUNC_DISPATCH = 4
FUNCKIND = tagFUNCKIND

tagCALLCONV = c_int
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
CALLCONV = tagCALLCONV

tagVARKIND = c_int
VAR_PERINSTANCE = 0
VAR_STATIC = 1
VAR_CONST = 2
VAR_DISPATCH = 3
VARKIND = tagVARKIND

################################################################
# forward declaration of com interfaces
#
# com method tables are at the end of the file

class IDispatch(IUnknown):
    pass

class IRecordInfo(IUnknown):
    pass

class ITypeInfo(IUnknown):
    pass

class ITypeComp(IUnknown):
    pass

class ITypeLib(IUnknown):
    pass

################################################################

class tagTLIBATTR(Structure):
    _fields_ = [
        ('guid', GUID),
        ('lcid', c_ulong),
        ('syskind', tagSYSKIND),
        ('wMajorVerNum', c_ushort),
        ('wMinorVerNum', c_ushort),
        ('wLibFlags', c_ushort),
]
TLIBATTR = tagTLIBATTR
assert sizeof(tagTLIBATTR) == 32, sizeof(tagTLIBATTR)
assert alignment(tagTLIBATTR) == 4, alignment(tagTLIBATTR)

class tagSAFEARRAYBOUND(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 226
    _fields_ = [
        ('cElements', c_ulong),
        ('lLbound', c_long),
    ]
assert sizeof(tagSAFEARRAYBOUND) == 8, sizeof(tagSAFEARRAYBOUND)
assert alignment(tagSAFEARRAYBOUND) == 4, alignment(tagSAFEARRAYBOUND)
SAFEARRAYBOUND = tagSAFEARRAYBOUND

class tagSAFEARRAY(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 321
    _fields_ = [
        ('cDims', c_ushort),
        ('fFeatures', c_ushort),
        ('cbElements', c_ulong),
        ('cLocks', c_ulong),
        ('pvData', c_void_p),
        ('rgsabound', tagSAFEARRAYBOUND * 1),
    ]
SAFEARRAY = tagSAFEARRAY
assert sizeof(tagSAFEARRAY) == 24, sizeof(tagSAFEARRAY)
assert alignment(tagSAFEARRAY) == 4, alignment(tagSAFEARRAY)

class tagEXCEPINFO(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 722
    pass
tagEXCEPINFO._fields_ = [
    ('wCode', c_ushort),
    ('wReserved', c_ushort),
    ('bstrSource', POINTER(c_wchar)),
    ('bstrDescription', POINTER(c_wchar)),
    ('bstrHelpFile', POINTER(c_wchar)),
    ('dwHelpContext', c_ulong),
    ('pvReserved', c_void_p),
    ('pfnDeferredFillIn', WINFUNCTYPE(c_long, POINTER(tagEXCEPINFO))),
    ('scode', c_long),
]
assert sizeof(tagEXCEPINFO) == 32, sizeof(tagEXCEPINFO)
assert alignment(tagEXCEPINFO) == 4, alignment(tagEXCEPINFO)
EXCEPINFO = tagEXCEPINFO # typedef C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 732

################################################################
# ARRAYDESC, TYPEDESC

class tagARRAYDESC(Structure):
    pass
ARRAYDESC = tagARRAYDESC

class tagTYPEDESC(Structure):
    pass
TYPEDESC = tagTYPEDESC

class _tagTYPEDESC_203E(Union):
    _fields_ = [
        ('lptdesc', POINTER(tagTYPEDESC)),
        ('lpadesc', POINTER(tagARRAYDESC)),
        ('hreftype', c_ulong),
    ]

tagTYPEDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 582
    # Unnamed field renamed to '_'
    ('_', _tagTYPEDESC_203E),
    ('vt', c_ushort),
]
assert sizeof(tagTYPEDESC) == 8, sizeof(tagTYPEDESC)
assert alignment(tagTYPEDESC) == 4, alignment(tagTYPEDESC)

tagARRAYDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 594
    ('tdescElem', tagTYPEDESC),
    ('cDims', c_ushort),
    ('rgbounds', tagSAFEARRAYBOUND * 1),
]
assert sizeof(tagARRAYDESC) == 20, sizeof(tagARRAYDESC)
assert alignment(tagARRAYDESC) == 4, alignment(tagARRAYDESC)

################################################################
## CURRENCY

# A fixed point decimal number, stored as integer scaled by 10000.
class tagCY(Union):
    class _tagCY_143E(Structure):
        _fields_ = [
            ('Lo', c_ulong),
            ('Hi', c_long),
        ]
    _fields_ = [
        # Unnamed field renamed to '_'
        ('_', _tagCY_143E),
        ('int64', c_longlong),
    ]

assert sizeof(tagCY) == 8, sizeof(tagCY)
assert alignment(tagCY) == 8, alignment(tagCY)
CY = tagCY
CURRENCY = tagCY

################################################################
# DECIMAL

# A fixed point decimal number, stored as 12-byte integer, scaled by
# scale which is between 0 and 28.  Sign stored separately.
class _tagDEC_144E(Union):
    class _tagDEC_1445DOLLAR_145E(Structure):
        _fields_ = [
            ('scale', c_ubyte),
            ('sign', c_ubyte),
        ]
    _fields_ = [
        # Unnamed field renamed to '_'
        ('_', _tagDEC_1445DOLLAR_145E),
        ('signscale', c_ushort),
    ]
assert sizeof(_tagDEC_144E) == 2, sizeof(_tagDEC_144E)
assert alignment(_tagDEC_144E) == 2, alignment(_tagDEC_144E)

class _tagDEC_146E(Union):
    class _tagDEC_1465DOLLAR_147E(Structure):
        _fields_ = [
            ('Lo32', c_ulong),
            ('Mid32', c_ulong),
        ]
    _fields_ = [
        # Unnamed field renamed to '_'
        ('_', _tagDEC_1465DOLLAR_147E),
        ('Lo64', c_ulonglong),
    ]
assert sizeof(_tagDEC_146E) == 8, sizeof(_tagDEC_146E)
assert alignment(_tagDEC_146E) == 8, alignment(_tagDEC_146E)

class tagDEC(Structure):
    _fields_ = [
        # C:/PROGRA~1/MICROS~3.NET/Vc7/PLATFO~1/Include/wtypes.h 1020
        ('wReserved', c_ushort),
        # Unnamed field renamed to '_'
        ('_', _tagDEC_144E),
        ('Hi32', c_ulong),
        # Unnamed field renamed to '_1'
        ('_1', _tagDEC_146E),
    ]
assert sizeof(tagDEC) == 16, sizeof(tagDEC)
assert alignment(tagDEC) == 8, alignment(tagDEC)

DECIMAL = tagDEC

################################################################
# VARIANT

class tagVARIANT(Structure):
    pass

class __tagVARIANT(Structure):
    class _201E(Union):
        class __tagBRECORD_(Structure):
            _fields_ = [
                ('pvRecord', c_void_p),
                ('pRecInfo', POINTER(IRecordInfo)),
            ]
        _fields_ = [ # union _201E
            ('llVal', c_longlong),
            ('lVal', c_long),
            ('bVal', c_ubyte),
            ('iVal', c_short),
            ('fltVal', c_float),
            ('dblVal', c_double),
            ('boolVal', c_short),
            ('scode', c_long),
            ('cyVal', tagCY),
            ('date', c_double),
            ('bstrVal', POINTER(c_wchar)),
            ('punkVal', POINTER(IUnknown)),
            ('pdispVal', POINTER(IDispatch)),
            ('parray', POINTER(tagSAFEARRAY)),
            ('pbVal', POINTER(c_ubyte)),
            ('piVal', POINTER(c_short)),
            ('plVal', POINTER(c_long)),
            ('pllVal', POINTER(c_longlong)),
            ('pfltVal', POINTER(c_float)),
            ('pdblVal', POINTER(c_double)),
            ('pboolVal', POINTER(c_short)),
            ('pscode', POINTER(c_long)),
            ('pcyVal', POINTER(tagCY)),
            ('pdate', POINTER(c_double)),
            ('pbstrVal', POINTER(POINTER(c_wchar))),
            ('ppunkVal', POINTER(POINTER(IUnknown))),
            ('ppdispVal', POINTER(POINTER(IDispatch))),
            ('pparray', POINTER(POINTER(tagSAFEARRAY))),
            ('pvarVal', POINTER(tagVARIANT)),
            ('byref', c_void_p),
            ('cVal', c_char),
            ('uiVal', c_ushort),
            ('ulVal', c_ulong),
            ('ullVal', c_ulonglong),
            ('intVal', c_int),
            ('uintVal', c_uint),
            ('pdecVal', POINTER(tagDEC)),
            ('pcVal', POINTER(c_char)),
            ('puiVal', POINTER(c_ushort)),
            ('pulVal', POINTER(c_ulong)),
            ('pullVal', POINTER(c_ulonglong)),
            ('pintVal', POINTER(c_int)),
            ('puintVal', POINTER(c_uint)),
            ('brecVal', __tagBRECORD_),
        ] # union _201E
    _fields_ = [ # __tagVARIANT
        ('vt', c_ushort),
        ('wReserved1', c_ushort),
        ('wReserved2', c_ushort),
        ('wReserved3', c_ushort),
        ('n3', _201E),
    ] # __tagVARIANT
assert sizeof(__tagVARIANT) == 16, sizeof(__tagVARIANT)
assert alignment(__tagVARIANT) == 8, alignment(__tagVARIANT)

class _tagVARIANT_200E(Union):
    pass
_tagVARIANT_200E._fields_ = [
    ('n2', __tagVARIANT),
    ('decVal', tagDEC),
]
assert sizeof(_tagVARIANT_200E) == 16, sizeof(_tagVARIANT_200E)
assert alignment(_tagVARIANT_200E) == 8, alignment(_tagVARIANT_200E)

tagVARIANT._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 424
    ('n1', _tagVARIANT_200E),
]
VARIANT = tagVARIANT
VARIANTARG = tagVARIANT
assert sizeof(tagVARIANT) == 16, sizeof(tagVARIANT)
assert alignment(tagVARIANT) == 8, alignment(tagVARIANT)

################################################################
# DISPPARAMS

class tagDISPPARAMS(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 696
    _fields_ = [
        ('rgvarg', POINTER(tagVARIANT)),
        ('rgdispidNamedArgs', POINTER(c_long)),
        ('cArgs', c_uint),
        ('cNamedArgs', c_uint),
    ]
DISPPARAMS = tagDISPPARAMS # typedef C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 701
assert sizeof(tagDISPPARAMS) == 16, sizeof(tagDISPPARAMS)
assert alignment(tagDISPPARAMS) == 4, alignment(tagDISPPARAMS)

################################################################

class tagIDLDESC(Structure):
    _fields_ = [
        ('dwReserved', c_ulong),
        ('wIDLFlags', c_ushort),
    ]
assert sizeof(tagIDLDESC) == 8, sizeof(tagIDLDESC)
assert alignment(tagIDLDESC) == 4, alignment(tagIDLDESC)
IDLDESC = tagIDLDESC # typedef C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 636

class tagTYPEATTR(Structure):
    _fields_ = [
        ('guid', GUID),
        ('lcid', c_ulong),
        ('dwReserved', c_ulong),
        ('memidConstructor', c_long),
        ('memidDestructor', c_long),
        ('lpstrSchema', POINTER(c_wchar)),
        ('cbSizeInstance', c_ulong),
        ('typekind', tagTYPEKIND),
        ('cFuncs', c_ushort),
        ('cVars', c_ushort),
        ('cImplTypes', c_ushort),
        ('cbSizeVft', c_ushort),
        ('cbAlignment', c_ushort),
        ('wTypeFlags', c_ushort),
        ('wMajorVerNum', c_ushort),
        ('wMinorVerNum', c_ushort),
        ('tdescAlias', tagTYPEDESC),
        ('idldescType', tagIDLDESC),
    ]
assert sizeof(tagTYPEATTR) == 76, sizeof(tagTYPEATTR)
assert alignment(tagTYPEATTR) == 4, alignment(tagTYPEATTR)
TYPEATTR = tagTYPEATTR # typedef C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 691

################################################################
# PARAMDESC, PARAMDESCEX
class tagPARAMDESC(Structure):
    pass

class tagPARAMDESCEX(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 601
    _fields_ = [
        ('cBytes', c_ulong),
        ('varDefaultValue', tagVARIANT),
]
assert sizeof(tagPARAMDESCEX) == 24, sizeof(tagPARAMDESCEX)
assert alignment(tagPARAMDESCEX) == 8, alignment(tagPARAMDESCEX)
PARAMDESCEX = tagPARAMDESCEX

tagPARAMDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 609
    ('pparamdescex', POINTER(tagPARAMDESCEX)),
    ('wParamFlags', c_ushort),
]
assert sizeof(tagPARAMDESC) == 8, sizeof(tagPARAMDESC)
assert alignment(tagPARAMDESC) == 4, alignment(tagPARAMDESC)
PARAMDESC = tagPARAMDESC

################################################################
# ELEMDESC

class tagELEMDESC(Structure):
    class _tagELEMDESC_204E(Union):
        _fields_ = [
            ('idldesc', tagIDLDESC),
            ('paramdesc', tagPARAMDESC),
        ]
    _fields_ = [
        ('tdesc', tagTYPEDESC),
        # Unnamed field renamed to '_'
        ('_', _tagELEMDESC_204E),
]
assert sizeof(tagELEMDESC) == 16, sizeof(tagELEMDESC)
assert alignment(tagELEMDESC) == 4, alignment(tagELEMDESC)
ELEMDESC = tagELEMDESC # typedef C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 667

################################################################

class tagVARDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 803
    class N10tagVARDESC5DOLLAR_205E(Union):
        _fields_ = [
            ('oInst', c_ulong),
            ('lpvarValue', POINTER(tagVARIANT)),
        ]
    _fields_ = [
        ('memid', c_long),
        ('lpstrSchema', POINTER(c_wchar)),
        # Unnamed field renamed to '_'
        ('_', N10tagVARDESC5DOLLAR_205E),
        ('elemdescVar', tagELEMDESC),
        ('wVarFlags', c_ushort),
        ('varkind', tagVARKIND),
    ]
assert sizeof(tagVARDESC) == 36, sizeof(tagVARDESC)
assert alignment(tagVARDESC) == 4, alignment(tagVARDESC)
VARDESC = tagVARDESC

################################################################
# FUNCDESC
class tagFUNCDESC(Structure):
    _fields_ = [
        # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 769
        ('memid', c_long),
        ('lprgscode', POINTER(c_long)),
        ('lprgelemdescParam', POINTER(tagELEMDESC)),
        ('funckind', tagFUNCKIND),
        ('invkind', tagINVOKEKIND),
        ('callconv', tagCALLCONV),
        ('cParams', c_short),
        ('cParamsOpt', c_short),
        ('oVft', c_short),
        ('cScodes', c_short),
        ('elemdescFunc', tagELEMDESC),
        ('wFuncFlags', c_ushort),
    ]
assert sizeof(tagFUNCDESC) == 52, sizeof(tagFUNCDESC)
assert alignment(tagFUNCDESC) == 4, alignment(tagFUNCDESC)
FUNCDESC = tagFUNCDESC

################################################################
# BINDPTR

class tagBINDPTR(Union):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 3075
    _fields_ = [
        ('lpfuncdesc', POINTER(tagFUNCDESC)),
        ('lpvardesc', POINTER(tagVARDESC)),
        ('lptcomp', POINTER(ITypeComp)),
    ]
assert sizeof(tagBINDPTR) == 4, sizeof(tagBINDPTR)
assert alignment(tagBINDPTR) == 4, alignment(tagBINDPTR)
BINDPTR = tagBINDPTR

################################################################
# COM interface method tables

IDispatch._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 2710
    STDMETHOD(c_long, 'GetTypeInfoCount', [POINTER(c_uint)]),
    STDMETHOD(c_long, 'GetTypeInfo', [c_uint, c_ulong, POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(c_long, 'GetIDsOfNames', [POINTER(GUID), POINTER(POINTER(c_wchar)), c_uint, c_ulong, POINTER(c_long)]),
    STDMETHOD(c_long, 'Invoke', [c_long, POINTER(GUID), c_ulong, c_ushort,
                                 POINTER(tagDISPPARAMS), POINTER(tagVARIANT), POINTER(tagEXCEPINFO), POINTER(c_uint)]),
]

IRecordInfo._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 5926
    STDMETHOD(c_long, 'RecordInit', [c_void_p]),
    STDMETHOD(c_long, 'RecordClear', [c_void_p]),
    STDMETHOD(c_long, 'RecordCopy', [c_void_p, c_void_p]),
    STDMETHOD(c_long, 'GetGuid', [POINTER(GUID)]),
    STDMETHOD(c_long, 'GetName', [POINTER(POINTER(c_wchar))]),
    STDMETHOD(c_long, 'GetSize', [POINTER(c_ulong)]),
    STDMETHOD(c_long, 'GetTypeInfo', [POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(c_long, 'GetField', [c_void_p, POINTER(c_wchar), POINTER(tagVARIANT)]),
    STDMETHOD(c_long, 'GetFieldNoCopy', [c_void_p, POINTER(c_wchar), POINTER(tagVARIANT), POINTER(c_void_p)]),
    STDMETHOD(c_long, 'PutField', [c_ulong, c_void_p, POINTER(c_wchar), POINTER(tagVARIANT)]),
    STDMETHOD(c_long, 'PutFieldNoCopy', [c_ulong, c_void_p, POINTER(c_wchar), POINTER(tagVARIANT)]),
    STDMETHOD(c_long, 'GetFieldNames', [POINTER(c_ulong), POINTER(POINTER(c_wchar))]),
    STDMETHOD(c_int, 'IsMatchingType', [POINTER(IRecordInfo)]),
    STDMETHOD(c_void_p, 'RecordCreate', []),
    STDMETHOD(c_long, 'RecordCreateCopy', [c_void_p, POINTER(c_void_p)]),
    STDMETHOD(c_long, 'RecordDestroy', [c_void_p]),
]

ITypeInfo._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 3230
    STDMETHOD(c_long, 'GetTypeAttr', [POINTER(POINTER(tagTYPEATTR))]),
    STDMETHOD(c_long, 'GetTypeComp', [POINTER(POINTER(ITypeComp))]),
    STDMETHOD(c_long, 'GetFuncDesc', [c_uint, POINTER(POINTER(tagFUNCDESC))]),
    STDMETHOD(c_long, 'GetVarDesc', [c_uint, POINTER(POINTER(tagVARDESC))]),
    STDMETHOD(c_long, 'GetNames', [c_long, POINTER(POINTER(c_wchar)), c_uint, POINTER(c_uint)]),
    STDMETHOD(c_long, 'GetRefTypeOfImplType', [c_uint, POINTER(c_ulong)]),
    STDMETHOD(c_long, 'GetImplTypeFlags', [c_uint, POINTER(c_int)]),
    STDMETHOD(c_long, 'GetIDsOfNames', [POINTER(POINTER(c_wchar)), c_uint, POINTER(c_long)]),
    STDMETHOD(c_long, 'Invoke', [c_void_p, c_long, c_ushort, POINTER(tagDISPPARAMS),
                                 POINTER(tagVARIANT), POINTER(tagEXCEPINFO), POINTER(c_uint)]),
    STDMETHOD(c_long, 'GetDocumentation', [c_long, POINTER(POINTER(c_wchar)),
                                           POINTER(POINTER(c_wchar)), POINTER(c_ulong), POINTER(POINTER(c_wchar))]),
    STDMETHOD(c_long, 'GetDllEntry', [c_long, tagINVOKEKIND,
                                      POINTER(POINTER(c_wchar)), POINTER(POINTER(c_wchar)), POINTER(c_ushort)]),
    STDMETHOD(c_long, 'GetRefTypeInfo', [c_ulong, POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(c_long, 'AddressOfMember', [c_long, tagINVOKEKIND, POINTER(c_void_p)]),
    STDMETHOD(c_long, 'CreateInstance', [POINTER(IUnknown), POINTER(GUID), POINTER(c_void_p)]),
    STDMETHOD(c_long, 'GetMops', [c_long, POINTER(POINTER(c_wchar))]),
    STDMETHOD(c_long, 'GetContainingTypeLib', [POINTER(POINTER(ITypeLib)), POINTER(c_uint)]),
    STDMETHOD(None, 'ReleaseTypeAttr', [POINTER(tagTYPEATTR)]),
    STDMETHOD(None, 'ReleaseFuncDesc', [POINTER(tagFUNCDESC)]),
    STDMETHOD(None, 'ReleaseVarDesc', [POINTER(tagVARDESC)]),
]

ITypeLib._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 4455
    STDMETHOD(c_uint, 'GetTypeInfoCount', []),
    STDMETHOD(c_long, 'GetTypeInfo', [c_uint, POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(c_long, 'GetTypeInfoType', [c_uint, POINTER(tagTYPEKIND)]),
    STDMETHOD(c_long, 'GetTypeInfoOfGuid', [POINTER(GUID), POINTER(POINTER(ITypeInfo))]),
    STDMETHOD(c_long, 'GetLibAttr', [POINTER(POINTER(tagTLIBATTR))]),
    STDMETHOD(c_long, 'GetTypeComp', [POINTER(POINTER(ITypeComp))]),
    STDMETHOD(c_long, 'GetDocumentation', [c_int, POINTER(POINTER(c_wchar)),
                                           POINTER(POINTER(c_wchar)), POINTER(c_ulong), POINTER(POINTER(c_wchar))]),
    STDMETHOD(c_long, 'IsName', [POINTER(c_wchar), c_ulong, POINTER(c_int)]),
    STDMETHOD(c_long, 'FindName', [POINTER(c_wchar), c_ulong,
                                   POINTER(POINTER(ITypeInfo)), POINTER(c_long), POINTER(c_ushort)]),
    STDMETHOD(None, 'ReleaseTLibAttr', [POINTER(tagTLIBATTR)]),
]

ITypeComp._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 3090
    STDMETHOD(c_long, 'Bind', [POINTER(c_wchar), c_ulong, c_ushort,
                               POINTER(POINTER(ITypeInfo)), POINTER(tagDESCKIND), POINTER(tagBINDPTR)]),
    STDMETHOD(c_long, 'BindType', [POINTER(c_wchar), c_ulong,
               POINTER(POINTER(ITypeInfo)), POINTER(POINTER(ITypeComp))]),
]
