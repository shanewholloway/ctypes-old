# comtypes.automation package

from ctypes import *
from _ctypes import CopyComPointer
from comtypes import IUnknown, GUID, IID, STDMETHOD, BSTR
import datetime # for VT_DATE, standard in Python 2.3 and up
try:
    import decimal # standard in Python 2.4 and up
except ImportError:
    decimal = None
    
from ctypes import _SimpleCData
class VARIANT_BOOL(_SimpleCData):
    _type_ = "v"
    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, self.value)
assert(sizeof(VARIANT_BOOL) == 2)

# these may be moved elsewhere...
WORD = c_ushort
UINT = c_uint
DWORD = c_ulong
LONG = c_long

WCHAR = c_wchar
LCID = DWORD
DISPID = LONG
SCODE = LONG

VARTYPE = c_ushort

################################
# helper constants
IID_NULL = GUID()
riid_null = byref(IID_NULL)
_oleaut32 = oledll.oleaut32
# 30. December 1899, midnight.  For VT_DATE.
_com_null_date = datetime.datetime(1899, 12, 30, 0, 0, 0)


################################################################
# VARIANT, in all it's glory.
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

class tagCY(Structure):
    _fields_ = [("int64", c_longlong)]
CY = tagCY
CURRENCY = CY

class tagVARIANT(Structure):
    # The C Header file defn of VARIANT is much more complicated, but
    # this is the ctypes version - functional as well.
    class U_VARIANT(Union):
        _fields_ = [
            ("VT_BOOL", VARIANT_BOOL),
            ("VT_I1", c_byte),
            ("VT_I2", c_short),
            ("VT_I4", c_long),
            ("VT_INT", c_int),
            ("VT_UI1", c_ubyte),
            ("VT_UI2", c_ushort),
            ("VT_UI4", c_ulong),
            ("VT_UINT", c_uint),
            ("VT_R4", c_float),
            ("VT_R8", c_double),
            ("VT_CY", c_longlong),
            ("c_wchar_p", c_wchar_p),
            ("c_void_p", c_void_p),

            ("bstrVal", BSTR),
            ]
    _fields_ = [("vt", VARTYPE),
                ("wReserved1", c_ushort),
                ("wReserved2", c_ushort),
                ("wReserved3", c_ushort),
                ("_", U_VARIANT)
    ]

    # see also c:/sf/pywin32/com/win32com/src/oleargs.cpp 54
    def _set_value(self, value):
        _oleaut32.VariantClear(byref(self))
        if value is None:
            self.vt = VT_NULL
        elif isinstance(value, int):
            self.vt = VT_I4
            self._.VT_I4 = value
        elif isinstance(value, long):
            self.vt = VT_I4
            u = self._
            u.VT_I4 = value
            if u.VT_I4 != value:
                self.vt = VT_R8
                u.VT_R8 = float(value)
        elif isinstance(value, float):
            self.vt = VT_R8
            self._.VT_R8 = value
        elif isinstance(value, unicode):
            self.vt = VT_BSTR
            self._.c_void_p = _oleaut32.SysAllocStringLen(value, len(value))
        elif isinstance(value, str):
            self.vt = VT_BSTR
            value = unicode(value)
            self._.c_void_p = _oleaut32.SysAllocStringLen(value, len(value))
        elif isinstance(value, bool):
            self.vt = VT_BOOL
            self._.VT_BOOL = value
        elif isinstance(value, datetime.datetime):
            delta = value - _com_null_date
            # a day has 24 * 60 * 60 = 86400 seconds
            com_days = delta.days + (delta.seconds + delta.microseconds * 1e-6) / 86400.
            self.vt = VT_DATE
            self._.VT_R8 = com_days
        elif decimal is not None and isinstance(value, decimal.Decimal):
            self._.VT_CY = int(round(value * 10000))
        elif isinstance(value, POINTER(IDispatch)):
            CopyComPointer(value, byref(self._))
            self.vt = VT_DISPATCH
        elif isinstance(value, POINTER(IUnknown)):
            CopyComPointer(value, byref(self._))
            self.vt = VT_UNKNOWN
        else:
            raise "NYI", value
        # buffer ->  SAFEARRAY of VT_UI1 ?

    # c:/sf/pywin32/com/win32com/src/oleargs.cpp 197
    def _get_value(self):
        vt = self.vt
        if vt in (VT_EMPTY, VT_NULL):
            return None
        elif vt == VT_I1:
            return self._.VT_I1
        elif vt == VT_I2:
            return self._.VT_I2
        elif vt == VT_I4:
            return self._.VT_I4
        elif vt == VT_INT:
            return self._.VT_INT
        elif vt == VT_UI1:
            return self._.VT_UI1
        elif vt == VT_UI2:
            return self._.VT_UI2
        elif vt == VT_UI4:
            return self._.VT_UI4
        elif vt == VT_UINT:
            return self._.VT_UINT
        elif vt == VT_R4:
            return self._.VT_R4
        elif vt == VT_R8:
            return self._.VT_R8
        elif vt == VT_BOOL:
            return self._.VT_BOOL
        elif vt == VT_BSTR:
            return self._.bstrVal or u''
        elif vt == VT_DATE:
            days = self._.VT_R8
            return datetime.timedelta(days=days) + _com_null_date
        elif vt == VT_CY:
            if decimal is not None:
                return self._.VT_CY / decimal.Decimal("10000")
            else:
                return self._.VT_CY / 10000.
        else:
            raise "NYI", vt

# these are missing:
##    getter[VT_ERROR]
##    getter[VT_ARRAY]
##    getter[VT_BYREF|VT_UI1]
##    getter[VT_BYREF|VT_I2]
##    getter[VT_BYREF|VT_I4]
##    getter[VT_BYREF|VT_R4]
##    getter[VT_BYREF|VT_R8]
##    getter[VT_BYREF|VT_BOOL]
##    getter[VT_BYREF|VT_ERROR]
##    getter[VT_BYREF|VT_CY]
##    getter[VT_BYREF|VT_DATE]
##    getter[VT_BYREF|VT_BSTR]
##    getter[VT_BYREF|VT_UNKNOWN]
##    getter[VT_BYREF|VT_DISPATCH]
##    getter[VT_BYREF|VT_ARRAY]
##    getter[VT_BYREF|VT_VARIANT]
##    getter[VT_BYREF]
##    getter[VT_BYREF|VT_DECIMAL]
##    getter[VT_BYREF|VT_I1]
##    getter[VT_BYREF|VT_UI2]
##    getter[VT_BYREF|VT_UI4]
##    getter[VT_BYREF|VT_INT]
##    getter[VT_BYREF|VT_UINT]

    value = property(_get_value, _set_value)

VARIANT = tagVARIANT
VARIANTARG = VARIANT

##from _ctypes import VARIANT_set
##import new
##VARIANT.value = property(VARIANT._get_value, new.instancemethod(VARIANT_set, None, VARIANT))


class tagEXCEPINFO(Structure):
    pass
tagEXCEPINFO._fields_ = [
    ('wCode', WORD),
    ('wReserved', WORD),
    ('bstrSource', BSTR),
    ('bstrDescription', BSTR),
    ('bstrHelpFile', BSTR),
    ('dwHelpContext', DWORD),
    ('pvReserved', c_void_p),
    ('pfnDeferredFillIn', WINFUNCTYPE(HRESULT, POINTER(tagEXCEPINFO))),
    ('scode', SCODE),
]
assert sizeof(tagEXCEPINFO) == 32, sizeof(tagEXCEPINFO)
assert alignment(tagEXCEPINFO) == 4, alignment(tagEXCEPINFO)
EXCEPINFO = tagEXCEPINFO

class tagDISPPARAMS(Structure):
    _fields_ = [
        # C:/Programme/gccxml/bin/Vc71/PlatformSDK/oaidl.h 696
        ('rgvarg', POINTER(VARIANTARG)),
        ('rgdispidNamedArgs', POINTER(DISPID)),
        ('cArgs', UINT),
        ('cNamedArgs', UINT),
    ]
assert sizeof(tagDISPPARAMS) == 16, sizeof(tagDISPPARAMS)
assert alignment(tagDISPPARAMS) == 4, alignment(tagDISPPARAMS)
DISPPARAMS = tagDISPPARAMS

DISPID_VALUE = 0
DISPID_UNKNOWN = -1
DISPID_PROPERTYPUT = -3
DISPID_NEWENUM = -4
DISPID_EVALUATE = -5
DISPID_CONSTRUCTOR = -6
DISPID_DESTRUCTOR = -7
DISPID_COLLECT = -8

class IDispatch(IUnknown):
    _iid_ = GUID("{00020400-0000-0000-C000-000000000046}")
    _methods_ = [
        STDMETHOD(HRESULT, 'GetTypeInfoCount', [POINTER(UINT)]),
        STDMETHOD(HRESULT, 'GetTypeInfo', [UINT, LCID, POINTER(c_void_p)]),
        STDMETHOD(HRESULT, 'GetIDsOfNames', [POINTER(IID), POINTER(c_wchar_p),
                                             UINT, LCID, POINTER(DISPID)]),
        STDMETHOD(HRESULT, 'Invoke', [DISPID, POINTER(IID), LCID, WORD,
                                      POINTER(DISPPARAMS), POINTER(VARIANT),
                                      POINTER(EXCEPINFO), POINTER(UINT)]),
    ]

    def GetTypeInfoCount(self):
        r = c_uint()
        self.__com_GetTypeInfoCount(byref(r))
        return r.value

    def GetTypeInfo(self, index, lcid=0):
        p = POINTER(IUnknown)()
        self.__com_GetTypeInfo(index, lcid, byref(p))
        return p

    def GetIDsOfNames(self, *names, **kw):
        lcid = kw.pop("lcid", 0)
        assert not kw
        arr = (c_wchar_p * len(names))(*names)
        ids = (DISPID * len(names))()
        self.__com_GetIDsOfNames(riid_null, arr, len(names), lcid, ids)
        return [i for i in ids]

    def Invoke(self, dispid, *args, **kw):
        _invkind = kw.pop("_invkind", 1) # DISPATCH_METHOD
        _lcid = kw.pop("_lcid", 0) 
        result = VARIANT()
        excepinfo = EXCEPINFO()
        argerr = c_uint()


        if _invkind == 1: # method
            dp = DISPPARAMS()
            dp.cArgs = len(args)
            dp.cNamedArgs = 0
            dp.rgvarg = (VARIANT * len(args))()
            for i, a in enumerate(args):
                dp.rgvarg[len(args) - i - 1].value = a
                
        elif _invkind == 4: # propput
            assert len(args) == 1
            dp = DISPPARAMS()
            dp.cArgs = 1
            dp.cNamedArgs = 1
            dp.rgvarg = pointer(VARIANT())
            dp.rgvarg[0].value = args[0]
            dp.rgdispidNamedArgs = pointer(DISPID(DISPID_PROPERTYPUT))

        try:
            self.__com_Invoke(dispid, riid_null, _lcid, _invkind, byref(dp),
                              byref(result), byref(excepinfo), byref(argerr))
        except WindowsError: # , details:
            # we should parse exception information now, depending on
            # the errno we got.  XXX Problem (?): error numbers are
            # signed integers, although in C the HRESULT values are
            # normally written in hex notation.
            raise


# all the DISP_E_ values from windows.h
DISP_E_BUFFERTOOSMALL = -2147352557
DISP_E_DIVBYZERO = -2147352558
DISP_E_NOTACOLLECTION = -2147352559
DISP_E_BADCALLEE = -2147352560
DISP_E_PARAMNOTOPTIONAL = -2147352561
DISP_E_BADPARAMCOUNT = -2147352562
DISP_E_ARRAYISLOCKED = -2147352563
DISP_E_UNKNOWNLCID = -2147352564
DISP_E_BADINDEX = -2147352565
DISP_E_OVERFLOW = -2147352566
DISP_E_EXCEPTION = -2147352567
DISP_E_BADVARTYPE = -2147352568
DISP_E_NONAMEDARGS = -2147352569
DISP_E_UNKNOWNNAME = -2147352570
DISP_E_TYPEMISMATCH = -2147352571
DISP_E_PARAMNOTFOUND = -2147352572
DISP_E_MEMBERNOTFOUND = -2147352573
DISP_E_UNKNOWNINTERFACE = -2147352575

################################################################

if __name__ == "__main__":
    oledll.ole32.CoInitialize(None)
    p = POINTER(IDispatch)()

    clsid = GUID.from_progid("InternetExplorer.Application")
    # Internet.Explorer
    oledll.ole32.CoCreateInstance(byref(clsid),
                                  None,
                                  7, # CLSCTX
                                  byref(p._iid_),
                                  byref(p))
    for i in range(p.GetTypeInfoCount()):
        result = p.GetTypeInfo(i)

    id_quit = p.GetIDsOfNames("Quit")[0]
    id_visible = p.GetIDsOfNames("Visible")[0]
    id_navigate = p.GetIDsOfNames("Navigate2")[0]
    print p.GetIDsOfNames("Navigate2", "URL", "Flags", "TargetFrameName", "PostData", "Headers")

    try:
        p.Invoke(id_visible, True, wFlags = 4)
        p.Invoke(id_navigate, "http://www.python.org/", 1)
        import time
        time.sleep(3)
        p.Invoke(id_quit, wFlags = 1)
##        p.Invoke(id_quit, True, wFlags = 1)
    finally:
        oledll.ole32.CoUninitialize()
