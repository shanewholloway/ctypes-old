from ctypes import *
from ctypes.com import IUnknown, GUID, CreateInstance, CLSCTX_LOCAL_SERVER, \
     CLSCTX_INPROC_SERVER, ole32, STDMETHOD, HRESULT
from ctypes.com.automation import IDispatch, ITypeInfo, FUNCDESC, VARDESC, \
     VARIANT, DISPPARAMS, IEnumVARIANT, oleaut32

DESCKIND = c_int

class ITypeComp(IUnknown):
    _iid_ = GUID("{00020403-0000-0000-C000-000000000046}")

class BINDPTR(Union):
    _fields_ = [("lpfuncdesc", POINTER(FUNCDESC)),
                ("lpvardesc", POINTER(VARDESC)),
                ("lptcomp", POINTER(ITypeComp))]

ITypeComp._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Bind", c_wchar_p, c_ulong, c_short,
              POINTER(POINTER(ITypeInfo)), POINTER(DESCKIND), POINTER(BINDPTR)),
    STDMETHOD(HRESULT, "BindType", c_wchar_p, c_ulong,
              POINTER(POINTER(ITypeInfo)), POINTER(POINTER(ITypeComp)))]

DISPATCH_METHOD = 0x1
DISPATCH_PROPERTYGET = 0x2
DISPATCH_PROPERTYPUT = 0x4
DISPATCH_PROPERTYPUTREF = 0x8

FUNC_VIRTUAL = 0
FUNC_PUREVIRTUAL = FUNC_VIRTUAL + 1
FUNC_NONVIRTUAL = FUNC_PUREVIRTUAL + 1
FUNC_STATIC = FUNC_NONVIRTUAL + 1
FUNC_DISPATCH = FUNC_STATIC + 1

DESCKIND_FUNCDESC = 1
DESCKIND_VARDESK = 2
DESCKIND_TYPECOMP = 3

DISPID_PROPERTYPUT = -3

guid_null = GUID()

def _wrap(variant):
    if variant.vt == 9: # VT_DISPATCH
        return _Dispatch(variant.value)
    return variant.value

class _Dispatch(object):
    def __init__(self, comobj):
        self.__dict__["comobj"] = comobj

        ti = POINTER(ITypeInfo)()
        self.comobj.GetTypeInfo(0, 0, byref(ti))
        tc = POINTER(ITypeComp)()
        ti.QueryInterface(byref(ITypeComp._iid_), byref(tc))

        self.__dict__["typecomp"] = tc

    def _get_funcdesc(self, name, flags):
        bp = BINDPTR()
        dk = DESCKIND()
        ti = POINTER(ITypeInfo)()
        self.typecomp.Bind(unicode(name),
                           0,
                           flags,
                           byref(ti),
                           byref(dk),
                           byref(bp))
        if dk.value != DESCKIND_FUNCDESC:
            return None
        fd = bp.lpfuncdesc[0]
        assert fd.funckind == FUNC_DISPATCH
        return fd

    def __prop_get(self, memid):
        result = VARIANT()
        self.comobj.Invoke(memid,
                           byref(guid_null),
                           0, # LCID
                           DISPATCH_PROPERTYGET,
                           byref(DISPPARAMS()),
                           byref(result),
                           None, # pExcepInfo
                           None) # puArgError
        return _wrap(result)

    def __prop_put(self, memid, value):
        parms = DISPPARAMS()
        parms.cArgs = 1
        parms.rgvarg = pointer(VARIANT(value))
        parms.cNamedArgs = 1
        parms.rgdispidNamedArgs = pointer(c_long(DISPID_PROPERTYPUT))
        self.comobj.Invoke(memid,
                           byref(guid_null),
                           0, # LCID
                           DISPATCH_PROPERTYPUT,
                           byref(parms),
                           None, # pVarResult
                           None, # pExcepInfo
                           None) # puArgError

    def __setattr__(self, name, value):
        fd = self._get_funcdesc(name, DISPATCH_PROPERTYPUT) # | DISPATCH_PROPERTYPUTREF)
        if fd is None:
            raise AttributeError, name
        assert fd.cParams == 1
        self.__prop_put(fd.memid, value)

    def __getattr__(self, name):
##        fd = self._get_funcdesc(name, DISPATCH_METHOD | DISPATCH_PROPERTYGET | DISPATCH_PROPERTYPUT)
        fd = self._get_funcdesc(name, DISPATCH_METHOD | DISPATCH_PROPERTYGET)# | DISPATCH_PROPERTYPUT)
        if fd is None:
            raise AttributeError, name
        if fd.invkind == DISPATCH_PROPERTYGET:
            if fd.cParams == 0:
                return self.__prop_get(fd.memid)
            return _DispMethod(self.comobj, fd)
        elif fd.invkind == DISPATCH_METHOD:
            return _DispMethod(self.comobj, fd)
        else:
            raise "What's this", fd.invkind

    def __call__(self):
        return self.__prop_get(0)

    def __len__(self):
        return self.Count

    def __getitem__(self, index):
        enum = POINTER(IEnumVARIANT)()
        self._NewEnum.QueryInterface(byref(IEnumVARIANT._iid_),
                                     byref(enum))
        if index:
            enum.Skip(index)
        result = VARIANT()
        enum.Next(1, byref(result), None)
        return _wrap(result)

    def __iter__(self):
        enum = POINTER(IEnumVARIANT)()
        self._NewEnum.QueryInterface(byref(IEnumVARIANT._iid_),
                                     byref(enum))
        return _NewEnum(enum)

class _NewEnum(object):
    def __init__(self, enum):
        self.enum = enum

    def __iter__(self):
        return self

    def next(self):
        result = VARIANT()
        self.enum.Next(1, byref(result), None)
        return _wrap(result)

class _DispMethod(object):
    def __init__(self, comobj, fd):
        self.comobj = comobj
        self.fd = fd

    def __call__(self, *args):
        parms = DISPPARAMS()
        parms.cArgs = len(args)
        array = (VARIANT * len(args))()
        for i, a in enumerate(args):
            array[i].value = a
        parms.rgvarg = array
        result = VARIANT()
        self.comobj.Invoke(self.fd.memid,
                           byref(guid_null),
                           0, # LCID
                           self.fd.invkind,
                           byref(parms),
                           byref(result), # pVarResult
                           None, # pExcepInfo
                           None) # puArgError
        return _wrap(result)

def Dispatch(progid, interface=IDispatch, clsctx=CLSCTX_INPROC_SERVER|CLSCTX_LOCAL_SERVER):
    guid = GUID.from_progid(unicode(progid))
    p = POINTER(interface)()
    ole32.CoCreateInstance(byref(guid),
                           None,
                           clsctx,
                           byref(interface._iid_),
                           byref(p))
    return _Dispatch(p)

################################################################

if __debug__:
    ##from win32com.client import Dispatch

    def test_word():
        try:
            word = Dispatch("Word.Application")
        except WindowsError, details:
            if details.errno == 0x800401F3L: # Invalid Class String
                print "It seems Word is not installed..."
                return
            raise

        word.Visible = 1

        doc = word.Documents.Add()
        wrange = doc.Range()
        for i in range(10):
            wrange.InsertAfter("Hello from ctypes via COM %d\n" % i)
        paras = doc.Paragraphs

        for i in range(len(paras)):
            p = paras[i]()
            p.Font.ColorIndex = i+1
            p.Font.Size = 12 + (2 * i)

    ##    for p in doc.Paragraphs:
    ##        p().Font.ColorIndex = i+1
    ##        p().Font.Size = 12 + (2 * i)

        import time
        time.sleep(1)

##        doc.Close(SaveChanges=0)
        doc.Close()

        word.Quit()

    if __name__ == "__main__":
        test_word()
