# generated by 'xml2py'
# flags '..\tools\windows.xml -m comtypes -m comtypes.automation -w -r .*TypeLibEx -r .*TypeLib -o typeinfo.py'
# then hacked manually
import weakref

from ctypes import *
from comtypes import STDMETHOD
from comtypes import _GUID, GUID
from comtypes.automation import BSTR
from comtypes.automation import DISPID
from comtypes.automation import DISPPARAMS
from comtypes.automation import DWORD
from comtypes.automation import EXCEPINFO
from comtypes.automation import HRESULT
from comtypes.automation import IID
from comtypes.automation import IUnknown
from comtypes.automation import IUnknown
from comtypes.automation import LCID
from comtypes.automation import LONG
from comtypes.automation import SCODE
from comtypes.automation import UINT
from comtypes.automation import VARIANT
from comtypes.automation import VARIANTARG
from comtypes.automation import VARTYPE
from comtypes.automation import WCHAR
from comtypes.automation import WORD
from comtypes.automation import tagVARIANT

BOOL = c_int
HREFTYPE = DWORD
INT = c_int
MEMBERID = DISPID
OLECHAR = WCHAR
PVOID = c_void_p
SHORT = c_short
ULONG_PTR = c_ulong
USHORT = c_ushort
LPOLESTR = POINTER(OLECHAR)

################################################################
# enums
tagSYSKIND = c_int # enum
SYS_WIN16 = 0
SYS_WIN32 = 1
SYS_MAC = 2
SYS_WIN64 = 3
SYSKIND = tagSYSKIND

tagREGKIND = c_int # enum
REGKIND_DEFAULT = 0
REGKIND_REGISTER = 1
REGKIND_NONE = 2
REGKIND = tagREGKIND

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
TYPEKIND = tagTYPEKIND

tagINVOKEKIND = c_int # enum
INVOKE_FUNC = 1
INVOKE_PROPERTYGET = 2
INVOKE_PROPERTYPUT = 4
INVOKE_PROPERTYPUTREF = 8
INVOKEKIND = tagINVOKEKIND

tagDESCKIND = c_int # enum
DESCKIND_NONE = 0
DESCKIND_FUNCDESC = 1
DESCKIND_VARDESC = 2
DESCKIND_TYPECOMP = 3
DESCKIND_IMPLICITAPPOBJ = 4
DESCKIND_MAX = 5
DESCKIND = tagDESCKIND

tagVARKIND = c_int # enum
VAR_PERINSTANCE = 0
VAR_STATIC = 1
VAR_CONST = 2
VAR_DISPATCH = 3
VARKIND = tagVARKIND

tagFUNCKIND = c_int # enum
FUNC_VIRTUAL = 0
FUNC_PUREVIRTUAL = 1
FUNC_NONVIRTUAL = 2
FUNC_STATIC = 3
FUNC_DISPATCH = 4
FUNCKIND = tagFUNCKIND

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
CALLCONV = tagCALLCONV

IMPLTYPEFLAG_FDEFAULT = 1
IMPLTYPEFLAG_FSOURCE = 2
IMPLTYPEFLAG_FRESTRICTED = 4
IMPLTYPEFLAG_FDEFAULTVTABLE = 8

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
TYPEFLAGS = tagTYPEFLAGS

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

PARAMFLAG_NONE = 0
PARAMFLAG_FIN = 1
PARAMFLAG_FOUT = 2
PARAMFLAG_FLCID = 4
PARAMFLAG_FRETVAL = 8
PARAMFLAG_FOPT = 16
PARAMFLAG_FHASDEFAULT = 32
PARAMFLAG_FHASCUSTDATA = 64

################################################################
# interfaces

class ITypeLib(IUnknown):
    _iid_ = GUID("{00020402-0000-0000-C000-000000000046}")

    def GetTypeInfoCount(self):
        "Return the number of type informations"
        return self.__com_GetTypeInfoCount()
    
    def GetTypeInfo(self, index):
        "Load type info by index"
        ti = POINTER(ITypeInfo)()
        self.__com_GetTypeInfo(index, byref(ti))
        return ti
    
    def GetTypeInfoType(self, index):
        "Return the TYPEKIND of type information"
        tkind = TYPEKIND()
        self.__com_GetTypeInfoType(index, byref(tkind))
        return tkind.value
    
    def GetTypeInfoOfGuid(self, guid):
        "Return type information for a guid"
        ti = POINTER(ITypeInfo)()
        self.__com_GetTypeInfoOfGuid(byref(guid), byref(ti))
        return ti

    def GetLibAttr(self):
        "Return type library attributes"
        ptla = POINTER(TLIBATTR)()
        self.__com_GetLibAttr(byref(ptla))
        result = ptla[0]
        result.__ref__ = weakref.ref(result, lambda dead: self.ReleaseTLibAttr(ptla))
        return result

    def GetTypeComp(self):
        "Return an ITypeComp pointer."
        tc = POINTER(ITypeComp)()
        self.__com_GetTypeComp(byref(tc))
        return tc

    def GetDocumentation(self, index):
        "Return documentation for a type description."
        name = BSTR()
        docstring = BSTR()
        helpcontext = DWORD()
        helpfile = BSTR()
        self.__com_GetDocumentation(index, byref(name), byref(docstring),
                                    byref(helpcontext), byref(helpfile))
        return name.value, docstring.value, helpcontext.value, helpfile.value
        
    def IsName(self, name, lHashVal=0):
        "Check if there is type information for this name"
        result = BOOL()
        self.__com_IsName(name, lHashVal, byref(result))
        return result.value

    def FindName(self, name, lHashVal=0):
        # Hm...
        found = c_ushort(1)
        tinfo = POINTER(ITypeInfo)()
        memid = MEMBERID()
        self.__com_FindName(name, lHashVal, byref(tinfo), byref(memid), byref(found))
        if found.value:
            return memid.value, tinfo

    def ReleaseTLibAttr(self, ptla):
        "Release TLIBATTR"
        self.__com_ReleaseTLibAttr(ptla)

################

class ITypeInfo(IUnknown):
    _iid_ = GUID("{00020401-0000-0000-C000-000000000046}")

    def GetTypeAttr(self):
        "Return TYPEATTR for this type"
        pta = POINTER(TYPEATTR)()
        self.__com_GetTypeAttr(byref(pta))
        result = pta[0]
        result.__ref__ = weakref.ref(result, lambda dead: self.ReleaseTypeAttr(pta))
        return result
        
    def GetTypeComp(self):
        "Return ITypeComp pointer for this type"
        tc = POINTER(ITypeComp)()
        self.__com_GetTypeComp(byref(tc))
        return tc
        
    def GetFuncDesc(self, index):
        "Return FUNCDESC for index"
        pfd = POINTER(FUNCDESC)()
        self.__com_GetFuncDesc(index, byref(pfd))
        fd = pfd[0]
        fd.__ref__ = weakref.ref(fd, lambda dead: self.ReleaseFuncDesc(pfd))
        return fd
    
    def GetVarDesc(self, index):
        "Return VARDESC for index"
        pvd = POINTER(VARDESC)()
        self.__com_GetVarDesc(index, byref(pvd))
        vd = pvd[0]
        vd.__ref__ = weakref.ref(vd, lambda dead: self.ReleaseVarDesc(pvd))
        return vd

    def GetNames(self, memid, count=1):
        "Return names for memid"
        names = (BSTR * count)()
        cnames = c_uint()
        self.__com_GetNames(memid, names, count, byref(cnames))
        return names[:cnames.value]

    def GetRefTypeOfImplType(self, index):
        "Get the reftype of an implemented type"
        href = HREFTYPE()
        self.__com_GetRefTypeOfImplType(index, byref(href))
        return href.value

    def GetImplTypeFlags(self, index):
        "Get IMPLTYPEFLAGS"
        flags = c_int()
        self.__com_GetImplTypeFlags(index, byref(flags))
        return flags.value

    def GetIDsOfNames(self, *names):
        "Maps function and argument names to identifiers"
        rgsznames = (c_wchar_p * len(names))(*names)
        ids = (MEMBERID * len(names))()
        self.__com_GetIDsOfNames(rgsznames, len(names), ids)
        return ids[:]


##    STDMETHOD(HRESULT, 'Invoke', [PVOID, MEMBERID, WORD, POINTER(DISPPARAMS), POINTER(VARIANT), POINTER(EXCEPINFO), POINTER(UINT)]),

    def GetDocumentation(self, memid):
        "Return documentation for a type"
        name = BSTR()
        docstring = BSTR()
        helpcontext = DWORD()
        helpfile = BSTR()
        self.__com_GetDocumentation(memid, byref(name), byref(docstring),
                                    byref(helpcontext), byref(helpfile))
        return name.value, docstring.value, helpcontext.value, helpfile.value

##    STDMETHOD(HRESULT, 'GetDllEntry', [MEMBERID, INVOKEKIND, POINTER(BSTR), POINTER(BSTR), POINTER(WORD)]),

    def GetRefTypeInfo(self, href):
        "Get type info for reftype"
        ti = POINTER(ITypeInfo)()
        self.__com_GetRefTypeInfo(href, byref(ti))
        return ti

##    STDMETHOD(HRESULT, 'AddressOfMember', [MEMBERID, INVOKEKIND, POINTER(PVOID)]),
##    STDMETHOD(HRESULT, 'CreateInstance', [POINTER(IUnknown), POINTER(IID), POINTER(PVOID)]),

    def GetMops(self, index):
        "Get marshalling opcodes (whatever that is...)"
        mops = BSTR()
        self.__com_GetMops(index, byref(mops))
        return mops.value

    def GetContainingTypeLib(self):
        "Return index into and the containing type lib itself"
        index = c_uint()
        tlib = POINTER(ITypeLib)()
        self.__com_GetContainingTypeLib(byref(tlib), byref(index))
        return index.value, tlib

    def ReleaseTypeAttr(self, pta):
        self.__com_ReleaseTypeAttr(pta)
        
    def ReleaseFuncDesc(self, pfd):
        self.__com_ReleaseFuncDesc(pfd)

    def ReleaseVarDesc(self, pvd):
        self.__com_ReleaseVarDesc(pvd)

################

class ITypeComp(IUnknown):
    _iid_ = GUID("{00020403-0000-0000-C000-000000000046}")

    def Bind(self, name, flags, lHashVal=0):
        "Bind to a name"
        bindptr = BINDPTR()
        desckind = DESCKIND()
        ti = POINTER(ITypeInfo)()
        self.__com_Bind(name, lHashVal, flags, byref(ti), byref(desckind), byref(bindptr))
        if desckind == DESCKIND_FUNCDESC:
            fd = bindptr.lpfuncdesc[0]
            fd.__ref__ = weakref.ref(fd, lambda dead: ti.ReleaseFuncDesc(bindptr.lpfuncdesc))
            return fd
        elif desckind == DESCKIND_VARDESC:
            vd = bindptr.lpvardesc[0]
            vd.__ref__ = weakref.ref(vd, lambda dead: ti.ReleaseVarDesc(bindptr.lpvardesc))
            return vd
        elif desckind == DESCKIND_TYPECOMP:
            return bindptr.lptcomp
        elif desckind == DESCKIND_IMPLICITAPPOBJ:
            raise "NYI"
        elif desckind == DESCKIND_NONE:
            return None
        
##    STDMETHOD(HRESULT, 'BindType', [LPOLESTR, DWORD, POINTER(POINTER(ITypeInfo)), POINTER(POINTER(ITypeComp))]),

################

class ICreateTypeLib(IUnknown):
    _iid_ = GUID("{00020406-0000-0000-C000-000000000046}")
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 2149

class ICreateTypeInfo(IUnknown):
    _iid_ = GUID("{00020405-0000-0000-C000-000000000046}")
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 915

################################################################
# functions

def LoadRegTypeLib(guid, wVerMajor, wVerMinor, lcid=0):
    "Load a registered type library"
    tlib = POINTER(ITypeLib)()
    LoadRegTypeLib._api_(byref(guid), wVerMajor, wVerMinor, lcid, byref(tlib))
    return tlib
LoadRegTypeLib = stdcall(HRESULT, 'oleaut32',
                         [POINTER(GUID), c_ushort, c_ushort, c_ulong, POINTER(POINTER(ITypeLib))]) (LoadRegTypeLib)

def LoadTypeLibEx(szFile, regkind=REGKIND_NONE):
    "Load, and optionally register a type library file"
    ptl = POINTER(ITypeLib)()
    LoadTypeLibEx._api_(szFile, regkind, byref(ptl))
    return ptl
LoadTypeLibEx = stdcall(HRESULT, 'oleaut32', [POINTER(OLECHAR), tagREGKIND, POINTER(POINTER(ITypeLib))]) (LoadTypeLibEx)

def LoadTypeLib(szFile):
    "Load and register a type library file"
    tlib = POINTER(ITypeLib)()
    LoadTypeLib._api_(szFile, byref(tlib))
    return tlib
LoadTypeLib = stdcall(HRESULT, 'oleaut32', [POINTER(OLECHAR), POINTER(POINTER(ITypeLib))]) (LoadTypeLib)

def UnRegisterTypeLib(libID, wVerMajor, wVerMinor, lcid=0, syskind=SYS_WIN32):
    "Unregister a registered type library"
    return UnRegisterTypeLib._api_(byref(libID), wVerMajor, wVerMinor, lcid, syskind)
UnRegisterTypeLib = stdcall(HRESULT, 'oleaut32',
                            [POINTER(GUID), c_ushort, c_ushort, c_ulong, tagSYSKIND]) (UnRegisterTypeLib)

def RegisterTypeLib(tlib, fullpath, helpdir=None):
    "Register a type library in the registry"
    return RegisterTypeLib._api_(tlib, fullpath, helpdir)
RegisterTypeLib = stdcall(HRESULT, 'oleaut32', [POINTER(ITypeLib), POINTER(OLECHAR), POINTER(OLECHAR)]) (RegisterTypeLib)


def CreateTypeLib(filename, syskind=SYS_WIN32):
    "Return a ICreateTypeLib pointer"
    ctlib = POINTER(ICreateTypeLib)()
    CreateTypeLib._api_(syskind, filename, byref(ctlib))
    return ctlib
CreateTypeLib = stdcall(HRESULT, 'oleaut32',
                        [tagSYSKIND, POINTER(OLECHAR), POINTER(POINTER(ICreateTypeLib))]) (CreateTypeLib)

def QueryPathOfRegTypeLib(libid, wVerMajor, wVerMinor, lcid=0):
    "Return the path of a registered type library"
    pathname = BSTR()
    QueryPathOfRegTypeLib._api_(byref(libid), wVerMajor, wVerMinor, lcid, byref(pathname))
    return pathname.value
QueryPathOfRegTypeLib = stdcall(HRESULT, 'oleaut32',
                                [POINTER(GUID), c_ushort, c_ushort, c_ulong, POINTER(BSTR)]) (QueryPathOfRegTypeLib)

################################################################
# Structures

class tagTLIBATTR(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 4437
    pass
TLIBATTR = tagTLIBATTR

class tagTYPEATTR(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 672
    pass
TYPEATTR = tagTYPEATTR
class tagFUNCDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 769
    pass
FUNCDESC = tagFUNCDESC
class tagVARDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 803
    pass
VARDESC = tagVARDESC

class tagBINDPTR(Union):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 3075
    pass
BINDPTR = tagBINDPTR
class tagTYPEDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 582
    pass
TYPEDESC = tagTYPEDESC
class tagIDLDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 633
    pass
IDLDESC = tagIDLDESC

class tagARRAYDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 594
    pass

################################################################
# interface vtbl definitions

ICreateTypeLib._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 2149
    STDMETHOD(HRESULT, 'CreateTypeInfo', [LPOLESTR, TYPEKIND, POINTER(POINTER(ICreateTypeInfo))]),
    STDMETHOD(HRESULT, 'SetName', [LPOLESTR]),
    STDMETHOD(HRESULT, 'SetVersion', [WORD, WORD]),
    STDMETHOD(HRESULT, 'SetGuid', [POINTER(GUID)]),
    STDMETHOD(HRESULT, 'SetDocString', [LPOLESTR]),
    STDMETHOD(HRESULT, 'SetHelpFileName', [LPOLESTR]),
    STDMETHOD(HRESULT, 'SetHelpContext', [DWORD]),
    STDMETHOD(HRESULT, 'SetLcid', [LCID]),
    STDMETHOD(HRESULT, 'SetLibFlags', [UINT]),
    STDMETHOD(HRESULT, 'SaveAllChanges', []),
]

ITypeLib._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 4455
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

ITypeInfo._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 3230
    STDMETHOD(HRESULT, 'GetTypeAttr', [POINTER(POINTER(TYPEATTR))]),
    STDMETHOD(HRESULT, 'GetTypeComp', [POINTER(POINTER(ITypeComp))]),
    STDMETHOD(HRESULT, 'GetFuncDesc', [UINT, POINTER(POINTER(FUNCDESC))]),
    STDMETHOD(HRESULT, 'GetVarDesc', [UINT, POINTER(POINTER(VARDESC))]),
    STDMETHOD(HRESULT, 'GetNames', [MEMBERID, POINTER(BSTR), UINT, POINTER(UINT)]),
    STDMETHOD(HRESULT, 'GetRefTypeOfImplType', [UINT, POINTER(HREFTYPE)]),
    STDMETHOD(HRESULT, 'GetImplTypeFlags', [UINT, POINTER(INT)]),
##    STDMETHOD(HRESULT, 'GetIDsOfNames', [POINTER(LPOLESTR), UINT, POINTER(MEMBERID)]),
    # this one changed, to accept c_wchar_p array
    STDMETHOD(HRESULT, 'GetIDsOfNames', [POINTER(c_wchar_p), UINT, POINTER(MEMBERID)]),
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

ITypeComp._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 3090
    STDMETHOD(HRESULT, 'Bind', [LPOLESTR, DWORD, WORD, POINTER(POINTER(ITypeInfo)), POINTER(DESCKIND), POINTER(BINDPTR)]),
    STDMETHOD(HRESULT, 'BindType', [LPOLESTR, DWORD, POINTER(POINTER(ITypeInfo)), POINTER(POINTER(ITypeComp))]),
]

ICreateTypeInfo._methods_ = [
# C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 915
    STDMETHOD(HRESULT, 'SetGuid', [POINTER(GUID)]),
    STDMETHOD(HRESULT, 'SetTypeFlags', [UINT]),
    STDMETHOD(HRESULT, 'SetDocString', [LPOLESTR]),
    STDMETHOD(HRESULT, 'SetHelpContext', [DWORD]),
    STDMETHOD(HRESULT, 'SetVersion', [WORD, WORD]),
    STDMETHOD(HRESULT, 'AddRefTypeInfo', [POINTER(ITypeInfo), POINTER(HREFTYPE)]),
    STDMETHOD(HRESULT, 'AddFuncDesc', [UINT, POINTER(FUNCDESC)]),
    STDMETHOD(HRESULT, 'AddImplType', [UINT, HREFTYPE]),
    STDMETHOD(HRESULT, 'SetImplTypeFlags', [UINT, INT]),
    STDMETHOD(HRESULT, 'SetAlignment', [WORD]),
    STDMETHOD(HRESULT, 'SetSchema', [LPOLESTR]),
    STDMETHOD(HRESULT, 'AddVarDesc', [UINT, POINTER(VARDESC)]),
    STDMETHOD(HRESULT, 'SetFuncAndParamNames', [UINT, POINTER(LPOLESTR), UINT]),
    STDMETHOD(HRESULT, 'SetVarName', [UINT, LPOLESTR]),
    STDMETHOD(HRESULT, 'SetTypeDescAlias', [POINTER(TYPEDESC)]),
    STDMETHOD(HRESULT, 'DefineFuncAsDllEntry', [UINT, LPOLESTR, LPOLESTR]),
    STDMETHOD(HRESULT, 'SetFuncDocString', [UINT, LPOLESTR]),
    STDMETHOD(HRESULT, 'SetVarDocString', [UINT, LPOLESTR]),
    STDMETHOD(HRESULT, 'SetFuncHelpContext', [UINT, DWORD]),
    STDMETHOD(HRESULT, 'SetVarHelpContext', [UINT, DWORD]),
    STDMETHOD(HRESULT, 'SetMops', [UINT, BSTR]),
    STDMETHOD(HRESULT, 'SetTypeIdldesc', [POINTER(IDLDESC)]),
    STDMETHOD(HRESULT, 'LayOut', []),
]

################################################################
# Structure fields

tagTLIBATTR._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 4437
    ('guid', GUID),
    ('lcid', LCID),
    ('syskind', SYSKIND),
    ('wMajorVerNum', WORD),
    ('wMinorVerNum', WORD),
    ('wLibFlags', WORD),
]
assert sizeof(tagTLIBATTR) == 32, sizeof(tagTLIBATTR)
assert alignment(tagTLIBATTR) == 4, alignment(tagTLIBATTR)
class N11tagTYPEDESC5DOLLAR_203E(Union):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 584
    pass
N11tagTYPEDESC5DOLLAR_203E._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 584
    ('lptdesc', POINTER(tagTYPEDESC)),
    ('lpadesc', POINTER(tagARRAYDESC)),
    ('hreftype', HREFTYPE),
]
assert sizeof(N11tagTYPEDESC5DOLLAR_203E) == 4, sizeof(N11tagTYPEDESC5DOLLAR_203E)
assert alignment(N11tagTYPEDESC5DOLLAR_203E) == 4, alignment(N11tagTYPEDESC5DOLLAR_203E)
tagTYPEDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 582
    # Unnamed field renamed to '_'
    ('_', N11tagTYPEDESC5DOLLAR_203E),
    ('vt', VARTYPE),
]
assert sizeof(tagTYPEDESC) == 8, sizeof(tagTYPEDESC)
assert alignment(tagTYPEDESC) == 4, alignment(tagTYPEDESC)
tagIDLDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 633
    ('dwReserved', ULONG_PTR),
    ('wIDLFlags', USHORT),
]
assert sizeof(tagIDLDESC) == 8, sizeof(tagIDLDESC)
assert alignment(tagIDLDESC) == 4, alignment(tagIDLDESC)
tagTYPEATTR._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 672
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
class N10tagVARDESC5DOLLAR_205E(Union):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 807
    pass
N10tagVARDESC5DOLLAR_205E._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 807
    ('oInst', DWORD),
    ('lpvarValue', POINTER(VARIANT)),
]
assert sizeof(N10tagVARDESC5DOLLAR_205E) == 4, sizeof(N10tagVARDESC5DOLLAR_205E)
assert alignment(N10tagVARDESC5DOLLAR_205E) == 4, alignment(N10tagVARDESC5DOLLAR_205E)
class tagELEMDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 661
    pass
class N11tagELEMDESC5DOLLAR_204E(Union):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 663
    pass

class tagPARAMDESC(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 609
    pass

class tagPARAMDESCEX(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 601
    pass
LPPARAMDESCEX = POINTER(tagPARAMDESCEX)

tagPARAMDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 609
    ('pparamdescex', LPPARAMDESCEX),
    ('wParamFlags', USHORT),
]
assert sizeof(tagPARAMDESC) == 8, sizeof(tagPARAMDESC)
assert alignment(tagPARAMDESC) == 4, alignment(tagPARAMDESC)
PARAMDESC = tagPARAMDESC

N11tagELEMDESC5DOLLAR_204E._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 663
    ('idldesc', IDLDESC),
    ('paramdesc', PARAMDESC),
]
assert sizeof(N11tagELEMDESC5DOLLAR_204E) == 8, sizeof(N11tagELEMDESC5DOLLAR_204E)
assert alignment(N11tagELEMDESC5DOLLAR_204E) == 4, alignment(N11tagELEMDESC5DOLLAR_204E)
tagELEMDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 661
    ('tdesc', TYPEDESC),
    # Unnamed field renamed to '_'
    ('_', N11tagELEMDESC5DOLLAR_204E),
]
assert sizeof(tagELEMDESC) == 16, sizeof(tagELEMDESC)
assert alignment(tagELEMDESC) == 4, alignment(tagELEMDESC)
ELEMDESC = tagELEMDESC

tagVARDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 803
    ('memid', MEMBERID),
    ('lpstrSchema', LPOLESTR),
    # Unnamed field renamed to '_'
    ('_', N10tagVARDESC5DOLLAR_205E),
    ('elemdescVar', ELEMDESC),
    ('wVarFlags', WORD),
    ('varkind', VARKIND),
]
assert sizeof(tagVARDESC) == 36, sizeof(tagVARDESC)
assert alignment(tagVARDESC) == 4, alignment(tagVARDESC)
tagBINDPTR._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 3075
    ('lpfuncdesc', POINTER(FUNCDESC)),
    ('lpvardesc', POINTER(VARDESC)),
    ('lptcomp', POINTER(ITypeComp)),
]
assert sizeof(tagBINDPTR) == 4, sizeof(tagBINDPTR)
assert alignment(tagBINDPTR) == 4, alignment(tagBINDPTR)

tagFUNCDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 769
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

tagPARAMDESCEX._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 601
    ('cBytes', DWORD),
    ('varDefaultValue', VARIANTARG),
]
assert sizeof(tagPARAMDESCEX) == 24, sizeof(tagPARAMDESCEX)
assert alignment(tagPARAMDESCEX) == 8, alignment(tagPARAMDESCEX)

class tagSAFEARRAYBOUND(Structure):
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 226
    _fields_ = [
        ('cElements', DWORD),
        ('lLbound', LONG),
    ]
assert sizeof(tagSAFEARRAYBOUND) == 8, sizeof(tagSAFEARRAYBOUND)
assert alignment(tagSAFEARRAYBOUND) == 4, alignment(tagSAFEARRAYBOUND)
SAFEARRAYBOUND = tagSAFEARRAYBOUND

tagARRAYDESC._fields_ = [
    # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 594
    ('tdescElem', TYPEDESC),
    ('cDims', USHORT),
    ('rgbounds', SAFEARRAYBOUND * 1),
]
assert sizeof(tagARRAYDESC) == 20, sizeof(tagARRAYDESC)
assert alignment(tagARRAYDESC) == 4, alignment(tagARRAYDESC)
