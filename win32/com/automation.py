from ctypes import *
from ctypes.wintypes import DWORD, WORD, LPOLESTR, LPCOLESTR
from ctypes.com import IUnknown, GUID, REFIID, REFGUID, STDMETHOD, HRESULT, \
     COMObject, CopyComPointer
from ctypes.com.hresult import *

from _ctypes import _Pointer

oleaut32 = oledll.oleaut32

################################################################
# types

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

################################################################
# Memory mamagement of BSTR is broken.
#
# The way we do them here, it is not possible to transfer the
# ownership of a BSTR instance.  ctypes allocates the memory with
# SysAllocString if we call the constructor with a string, and the
# instance calls SysFreeString when it is destroyed.
# So BSTR's received from dll function calls will never be freed,
# and BSTR's we pass to functions are freed too often ;-(

from _ctypes import _SimpleCData

class BSTR(_SimpleCData):
    _type_ = "X"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)

assert(sizeof(BSTR) == 4)

################################################################
# Interfaces declarations
#

DESCKIND = c_int

class ITypeComp(IUnknown):
    _iid_ = GUID("{00020403-0000-0000-C000-000000000046}")

class ITypeInfo(IUnknown):
    _iid_ = GUID("{00020401-0000-0000-C000-000000000046}")
                 
class ITypeLib(IUnknown):
    _iid_ = GUID("{00020402-0000-0000-C000-000000000046}")

class IDispatch(IUnknown):
    _iid_ = GUID("{00020400-0000-0000-C000-000000000046}")

PIDispatch = POINTER(IDispatch)

################################################################
# VARIANT
"""
/*
 * VARENUM usage key,
 *
 * * [V] - may appear in a VARIANT
 * * [T] - may appear in a TYPEDESC
 * * [P] - may appear in an OLE property set
 * * [S] - may appear in a Safe Array
 *
 *
 *  VT_EMPTY            [V]   [P]     nothing
 *  VT_NULL             [V]   [P]     SQL style Null
 *  VT_I2               [V][T][P][S]  2 byte signed int
 *  VT_I4               [V][T][P][S]  4 byte signed int
 *  VT_R4               [V][T][P][S]  4 byte real
 *  VT_R8               [V][T][P][S]  8 byte real
 *  VT_CY               [V][T][P][S]  currency
 *  VT_DATE             [V][T][P][S]  date
 *  VT_BSTR             [V][T][P][S]  OLE Automation string
 *  VT_DISPATCH         [V][T][P][S]  IDispatch *
 *  VT_ERROR            [V][T][P][S]  SCODE
 *  VT_BOOL             [V][T][P][S]  True=-1, False=0
 *  VT_VARIANT          [V][T][P][S]  VARIANT *
 *  VT_UNKNOWN          [V][T]   [S]  IUnknown *
 *  VT_DECIMAL          [V][T]   [S]  16 byte fixed point
 *  VT_RECORD           [V]   [P][S]  user defined type
 *  VT_I1               [V][T][P][s]  signed char
 *  VT_UI1              [V][T][P][S]  unsigned char
 *  VT_UI2              [V][T][P][S]  unsigned short
 *  VT_UI4              [V][T][P][S]  unsigned short
 *  VT_I8                  [T][P]     signed 64-bit int
 *  VT_UI8                 [T][P]     unsigned 64-bit int
 *  VT_INT              [V][T][P][S]  signed machine int
 *  VT_UINT             [V][T]   [S]  unsigned machine int
 *  VT_VOID                [T]        C style void
 *  VT_HRESULT             [T]        Standard return type
 *  VT_PTR                 [T]        pointer type
 *  VT_SAFEARRAY           [T]        (use VT_ARRAY in VARIANT)
 *  VT_CARRAY              [T]        C style array
 *  VT_USERDEFINED         [T]        user defined type
 *  VT_LPSTR               [T][P]     null terminated string
 *  VT_LPWSTR              [T][P]     wide null terminated string
 *  VT_FILETIME               [P]     FILETIME
 *  VT_BLOB                   [P]     Length prefixed bytes
 *  VT_STREAM                 [P]     Name of the stream follows
 *  VT_STORAGE                [P]     Name of the storage follows
 *  VT_STREAMED_OBJECT        [P]     Stream contains an object
 *  VT_STORED_OBJECT          [P]     Storage contains an object
 *  VT_BLOB_OBJECT            [P]     Blob contains an object 
 *  VT_CF                     [P]     Clipboard format
 *  VT_CLSID                  [P]     A Class ID
 *  VT_VECTOR                 [P]     simple counted array
 *  VT_ARRAY            [V]           SAFEARRAY*
 *  VT_BYREF            [V]           void* for local use
 *  VT_BSTR_BLOB                      Reserved for system use
 */
"""
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
VT_I8 = 20 # not allowed in VARIANT
VT_UI8 = 21 # not allowed in VARIANT
VT_INT = 22
VT_UINT = 23
VT_VOID = 24 # not allowed in VARIANT
VT_HRESULT = 25 # not allowed in VARIANT
VT_PTR = 26 # not allowed in VARIANT
VT_SAFEARRAY = 27 # not allowed in VARIANT
VT_CARRAY = 28 # not allowed in VARIANT
VT_USERDEFINED = 29 # not allowed in VARIANT
VT_LPSTR = 30 # not allowed in VARIANT
VT_LPWSTR = 31 # not allowed in VARIANT
VT_RECORD = 36
VT_FILETIME = 64 # not allowed in VARIANT
VT_BLOB = 65 # not allowed in VARIANT
VT_STREAM = 66 # not allowed in VARIANT
VT_STORAGE = 67 # not allowed in VARIANT
VT_STREAMED_OBJECT = 68 # not allowed in VARIANT
VT_STORED_OBJECT = 69 # not allowed in VARIANT
VT_BLOB_OBJECT = 70 # not allowed in VARIANT
VT_CF = 71 # not allowed in VARIANT
VT_CLSID = 72 # not allowed in VARIANT
VT_BSTR_BLOB = 0xfff # not allowed in VARIANT
VT_VECTOR = 0x1000 # not allowed in VARIANT
VT_ARRAY = 0x2000
VT_BYREF = 0x4000
# VT_RESERVED = 0x8000
# VT_ILLEGAL = 0xffff
# VT_ILLEGALMASKED = 0xfff
VT_TYPEMASK = 0xfff

"""
/* VARIANT STRUCTURE
 *
 *  VARTYPE vt;
 *  WORD wReserved1;
 *  WORD wReserved2;
 *  WORD wReserved3;
 *  union {
 *    LONG           VT_I4
 *    BYTE           VT_UI1
 *    SHORT          VT_I2
 *    FLOAT          VT_R4
 *    DOUBLE         VT_R8
 *    VARIANT_BOOL   VT_BOOL
 *    SCODE          VT_ERROR
 *    CY             VT_CY
 *    DATE           VT_DATE
 *    BSTR           VT_BSTR
 *    IUnknown *     VT_UNKNOWN
 *    IDispatch *    VT_DISPATCH
 *    SAFEARRAY *    VT_ARRAY
 *    BYTE *         VT_BYREF|VT_UI1
 *    SHORT *        VT_BYREF|VT_I2
 *    LONG *         VT_BYREF|VT_I4
 *    FLOAT *        VT_BYREF|VT_R4
 *    DOUBLE *       VT_BYREF|VT_R8
 *    VARIANT_BOOL * VT_BYREF|VT_BOOL
 *    SCODE *        VT_BYREF|VT_ERROR
 *    CY *           VT_BYREF|VT_CY
 *    DATE *         VT_BYREF|VT_DATE
 *    BSTR *         VT_BYREF|VT_BSTR
 *    IUnknown **    VT_BYREF|VT_UNKNOWN
 *    IDispatch **   VT_BYREF|VT_DISPATCH
 *    SAFEARRAY **   VT_BYREF|VT_ARRAY
 *    VARIANT *      VT_BYREF|VT_VARIANT
 *    PVOID          VT_BYREF (Generic ByRef)
 *    CHAR           VT_I1
 *    USHORT         VT_UI2
 *    ULONG          VT_UI4
 *    INT            VT_INT
 *    UINT           VT_UINT
 *    DECIMAL *      VT_BYREF|VT_DECIMAL
 *    CHAR *         VT_BYREF|VT_I1
 *    USHORT *       VT_BYREF|VT_UI2
 *    ULONG *        VT_BYREF|VT_UI4
 *    INT *          VT_BYREF|VT_INT
 *    UINT *         VT_BYREF|VT_UINT
 *  }
 */
"""

class VARIANT(Structure):
    class U(Union):
        _fields_ = [("VT_BOOL", c_short),
                    ("VT_I1", c_char),
                    ("VT_I2", c_short),
                    ("VT_I4", c_long),
                    ("VT_INT", c_int),
                    ("VT_R4", c_float),
                    ("VT_R8", c_double),
                    ("VT_SCODE", c_ulong),
                    ("VT_UI1", c_byte),
                    ("VT_UI2", c_ushort),
                    ("VT_UI4", c_ulong),
                    ("VT_UINT", c_uint),
                    # These fields are not defined or used, accessing
                    # them is too dangerous.  We simply copy COM
                    # pointers out and in with the CopyComPointer
                    # function, and for BSTR we use the faked
                    # c_wchar_p field, and call SysAllocString
                    # outselves.
                    #("VT_DISPATCH", POINTER(IDispatch)),
                    #("VT_UNKNOWN", POINTER(IUnknown)),
                    ##("VT_BSTR", BSTR),

                    # faked fields, only for our convenience:
                    ("wstrVal", c_wchar_p),
                    ("voidp", c_void_p),
                    ]
    _fields_ = [("vt", VARTYPE),
                ("wReserved1", c_ushort),
                ("wReserved2", c_ushort),
                ("wReserved3", c_ushort),
                ("_", U)]

    # we want to be able to create uninitialized VARIANTs, but we also
    # want to create them with None as argument.
    def __init__(self, *args):
        if args[1:]:
            raise TypeError, "__init__() takes at most 2 arguments (%d given)" % (len(args) + 1)
        if args:
            self.value = args[0]

    def _set_value(self, value):
        typ = type(value)
        if typ is int:
            oleaut32.VariantClear(byref(self))
            self.vt = VT_INT
            self._.VT_INT = value
        elif typ is float:
            oleaut32.VariantClear(byref(self))
            self.vt = VT_R8
            self._.VT_R8 = value
        elif typ is str:
            oleaut32.VariantClear(byref(self))
            self.vt = VT_BSTR
            self._.voidp = oleaut32.SysAllocString(unicode(value))
        elif typ is unicode:
            oleaut32.VariantClear(byref(self))
            self.vt = VT_BSTR
            self._.voidp = oleaut32.SysAllocString(value)
        elif value is None:
            oleaut32.VariantClear(byref(self))
        elif typ is bool:
            oleaut32.VariantClear(byref(self))
            self.vt = VT_BOOL
            self._.VT_BOOL = value and -1 or 0
        elif typ is POINTER(IDispatch) \
                 or isinstance(value, _Pointer) and issubclass(typ._type_, IDispatch):
            # It is a POINTER(IDispatch or IDispatch subclass)
            oleaut32.VariantClear(byref(self))
            CopyComPointer(value, byref(self._))
            self.vt = VT_DISPATCH
        elif typ is POINTER(IUnknown) \
                 or isinstance(value, _Pointer) and issubclass(typ._type_, IUnknown):
            # It is a POINTER(IUnknown or IUnknown subclass)
            oleaut32.VariantClear(byref(self))
            CopyComPointer(value, byref(self._))
            self.vt = VT_UNKNOWN
        else:
            raise TypeError, "don't know how to store %r in a VARIANT" % value

    def _get_value(self):
        if self.vt == VT_EMPTY:
            return None
        elif self.vt == VT_I1:
            return self._.VT_I1
        elif self.vt == VT_I2:
            return self._.VT_I2
        elif self.vt == VT_I4:
            return self._.VT_I4
        elif self.vt == VT_UI1:
            return self._.VT_UI1
        elif self.vt == VT_UI2:
            return self._.VT_UI2
        elif self.vt == VT_UI4:
            return self._.VT_UI4
        elif self.vt == VT_INT:
            return self._.VT_INT
        elif self.vt == VT_UINT:
            return self._.VT_UINT
        elif self.vt == VT_R4:
            return self._.VT_R4
        elif self.vt == VT_R8:
            return self._.VT_R8
        elif self.vt == VT_BSTR:
            return self._.wstrVal
        # This code can be enabled again when all the POINTER(ISomeInterface)
        # classes have a constructor that calls AddRef() if not-null.
##        elif self.vt == VT_UNKNOWN:
##            return self._.VT_UNKNOWN
##        elif self.vt == VT_DISPATCH:
##            return self._.VT_DISPATCH
        elif self.vt == VT_UNKNOWN:
            p = POINTER(IUnknown)()
            CopyComPointer(self._.voidp, byref(p))
            return p
        elif self.vt == VT_DISPATCH:
            p = POINTER(IDispatch)()
            CopyComPointer(self._.voidp, byref(p))
            return p
        elif self.vt == VT_BOOL:
            return bool(self._.VT_BOOL)
        elif self.vt & VT_BYREF:
            # XXX Is this correct?  Shall we dereference the variant and return the result,
            # or should we return a POINTER to a VARIANT?
            return VARIANT.from_address(self._.voidp)
        elif self.vt == VT_ERROR:
            return ("Error", self._.VT_SCODE)
        elif self.vt == VT_NULL:
            return None
        else:
            raise TypeError, "don't know how to convert typecode %d" % self.vt
        # not yet done:
        # VT_ARRAY
        # VT_CY
        # VT_DATE

    value = property(_get_value, _set_value)

    def __repr__(self):
        return "<VARIANT 0x%X at %x>" % (self.vt, addressof(self))

    # We must do this manually, BUT ONLY if we own the VARIANT
##    def __del__(self, _clear = oleaut32.VariantClear):
##        _clear(byref(self))

    def optional(cls):
        var = VARIANT()
        var.vt = VT_ERROR
        var._.VT_SCODE = 0x80020004L
        return var
    optional = classmethod(optional)

assert(sizeof(VARIANT) == 16)

################################################################

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
                ("pvReserved", c_void_p),
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
LPADESC = POINTER("ARRAYDESC")

class TYPEDESC(Structure):
    class U(Union):
        _fields_ = [("lptdesc", LPTYPEDESC),
                    ("lpadesc", LPADESC),
                    ("hreftype", HREFTYPE)]
    _fields_ = [("u", U),
                ("vt", VARTYPE)]
assert(sizeof(TYPEDESC) == 8), sizeof(TYPEDESC)

class ARRAYDESC(Structure):
    _fields_ = [("tdescElem", TYPEDESC),
                ("cDims", c_ushort),
                # XXX Variable length array containing one element for
                # each dimension
                #
                # Hack: We limit ourself to 8-dimensional arrays,
                # and client code must make sure it doesn't access more than
                # cDims elements in this array.
                ("rgbounds", c_int * 8)]

LPADESC.set_type(ARRAYDESC)
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

class BINDPTR(Union):
    _fields_ = [("lpfuncdesc", POINTER(FUNCDESC)),
                ("lpvardesc", POINTER(VARDESC)),
                ("lptcomp", POINTER(ITypeComp))]

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

ITypeComp._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Bind", c_wchar_p, c_ulong, c_short,
              POINTER(POINTER(ITypeInfo)), POINTER(DESCKIND), POINTER(BINDPTR)),
    STDMETHOD(HRESULT, "BindType", c_wchar_p, c_ulong,
              POINTER(POINTER(ITypeInfo)), POINTER(POINTER(ITypeComp)))]

ITypeInfo._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "GetTypeAttr", POINTER(LPTYPEATTR)),
    STDMETHOD(HRESULT, "GetTypeComp", POINTER(POINTER(ITypeComp))),
    STDMETHOD(HRESULT, "GetFuncDesc", c_uint,  POINTER(POINTER(FUNCDESC))),
    STDMETHOD(HRESULT, "GetVarDesc", c_uint, POINTER(POINTER(VARDESC))),
    STDMETHOD(HRESULT, "GetNames", MEMBERID, POINTER(BSTR), c_uint, POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetRefTypeOfImplType", c_uint, POINTER(HREFTYPE)),
    STDMETHOD(HRESULT, "GetImplTypeFlags", c_uint, POINTER(IMPLTYPEFLAGS)),
    STDMETHOD(HRESULT, "GetIDsOfNames", POINTER(LPOLESTR), c_uint, POINTER(c_int)),
    STDMETHOD(HRESULT, "Invoke", POINTER(IUnknown), MEMBERID, WORD, POINTER(DISPPARAMS),
              POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(c_uint)),
    STDMETHOD(HRESULT, "GetDocumentation", MEMBERID, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ulong), POINTER(BSTR)),
    STDMETHOD(HRESULT, "GetDllEntry", MEMBERID, c_int, POINTER(BSTR), POINTER(BSTR),
              POINTER(c_ushort)),
    STDMETHOD(HRESULT, "GetRefTypeInfo", HREFTYPE, POINTER(POINTER(ITypeInfo))),
    STDMETHOD(HRESULT, "AddressOfMember", MEMBERID, c_int, POINTER(c_void_p)),
    STDMETHOD(HRESULT, "CreateInstance", c_void_p, REFIID, POINTER(POINTER(IUnknown))),
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
    STDMETHOD(HRESULT, "GetTypeComp", POINTER(POINTER(ITypeComp))),
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
    p = POINTER(ITypeLib)()
    oleaut32.LoadTypeLib(unicode(fnm), byref(p))
    return p

def LoadTypeLibEx(fnm, regkind=REGKIND_NONE):
    p = POINTER(ITypeLib)()
    oleaut32.LoadTypeLibEx(unicode(fnm), regkind, byref(p))
    return p

def LoadRegTypeLib(guid, wVerMajor, wVerMinor, lcid=0):
    p = POINTER(ITypeLib)()
    oleaut32.LoadRegTypeLib(byref(guid), wVerMajor, wVerMinor, lcid, byref(p))
    return p

################################################################

class DualObjImpl(COMObject):

    def __init__(self):
        COMObject.__init__(self)
        try:
            self.LoadTypeInfo()
        except WindowsError:
            # Do we want to see the exception? Not clear...
            import traceback
            traceback.print_exc()
            # continue without typeinfo
            self.typeinfo = None

    def LoadTypeInfo(self):
        interface = self._com_interfaces_[0]
        tlib = LoadRegTypeLib(self._typelib_.guid,
                              self._typelib_.version[0],
                              self._typelib_.version[1])
        typeinfo = POINTER(ITypeInfo)()
        tlib.GetTypeInfoOfGuid(byref(interface._iid_), byref(typeinfo))
        self.typeinfo = typeinfo

    # IDispatch methods

    def GetIDsOfNames(self, this, riid, rgszNames, cNames, lcid, rgDispid):
        if self.typeinfo is None:
            return E_NOTIMPL
        # We use windll.oleaut32 instead of oledll.oleaut32 because
        # we don't want an exception here, instead we pass the returned HRESULT
        # value to the caller.
        return windll.oleaut32.DispGetIDsOfNames(self.typeinfo, rgszNames,
                                                 cNames, rgDispid)

    def Invoke(self, this, dispid, refiid, lcid, wFlags,
               pDispParams, pVarResult, pExcepInfo, puArgErr):
        if self.typeinfo is None:
            return E_NOTIMPL
        # See the comment in GetIDsOfNames
        return windll.oleaut32.DispInvoke(this, self.typeinfo, dispid,
                                          wFlags, pDispParams,
                                          pVarResult, pExcepInfo, puArgErr)

    def GetTypeInfoCount(self, this, pctInfo):
        if pctInfo:
            pctInfo[0] = self.typeinfo is not None
        return S_OK

    def GetTypeInfo(self, this, index, lcid, ppTInfo):
        if self.typeinfo is None:
            return E_NOTIMPL
        # *ppTInfo = self.typeinfo
        return CopyComPointer(self.typeinfo, ppTInfo)

################################################################
# The following two are used by the readtlb tool

class dispinterface(IDispatch):
    class __metaclass__(type(IDispatch)):
        def __setattr__(self, name, value):
            if name == '_dispmethods_':
                dispmap = {}
                for dispid, mthname, proto in value:
                    dispmap[dispid] = mthname
                setattr(self, '_methods_', IDispatch._methods_)
                type(IDispatch).__setattr__(self, '_dispmap_', dispmap)
            type(IDispatch).__setattr__(self, name, value)

def DISPMETHOD(dispid, restype, name, *argtypes):
    return dispid, name, STDMETHOD(HRESULT, name, *argtypes)

################################################################
# some more automation COM interfaces
class IEnumVARIANT(IUnknown):
    _iid_ = GUID("{00020404-0000-0000-C000-000000000046}")

IEnumVARIANT._methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "Next", c_ulong, POINTER(VARIANT), POINTER(c_ulong)),
        STDMETHOD(HRESULT, "Skip", c_ulong),
        STDMETHOD(HRESULT, "Reset"),
        STDMETHOD(HRESULT, "Clone", POINTER(POINTER(IEnumVARIANT)))
        ]

class IErrorLog(IUnknown):
    _iid_ = GUID("{3127CA40-446E-11CE-8135-00AA004BB851}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "AddError", LPCOLESTR, POINTER(EXCEPINFO))
        ]

################################################################
# test code

if __debug__:
    if __name__ == "__main__":
        print repr(VARIANT("String").value)
        print repr(VARIANT(u"Unicode").value)

        v = VARIANT(False)
        print repr(v.value), v._.VT_BOOL

        v = VARIANT(True)
        print repr(v.value), v._.VT_BOOL

        print VARIANT.optional().value
        print VARIANT().value

        tlb = LoadTypeLibEx(r"c:\windows\system32\shdocvw.dll")
        v = VARIANT(tlb)
        print v.value, (tlb.AddRef(), tlb.Release())
        v.value = tlb
        print v.value, (tlb.AddRef(), tlb.Release())
        v.value = u"-1"
        print v.value, (tlb.AddRef(), tlb.Release())

        v.value = 42
        for i in range(32):
            dst = VARIANT()
            try:
                oleaut32.VariantChangeType(byref(dst), byref(v), 0, i)
            except WindowsError, detail:
                print i, detail
            else:
                try:
                    x = dst.value
                except:
                    pass
                else:
                    print i, repr(dst.value)
