from ctypes.com import IUnknown, PIUnknown, COMObject, ole32, \
     GUID, HRESULT, STDMETHOD, REFIID
from ctypes.com.automation import IDispatch, oleaut32
from ctypes import c_int, c_ulong, byref, c_voidp, Structure, windll, POINTER, pointer

user32 = windll.user32
ole32.CoInitialize(None)

# We need to call this when we're done:
import atexit
atexit.register(ole32.CoUninitialize)

S_OK = 0
E_NOTIMPL = 0x80004001
E_NOINTERFACE = 0x80004002

DWORD = c_ulong

CLASS_E_NOAGGREGATION = 0x80040110
CLASS_E_CLASSNOTAVAILABLE = 0x80040111

EXTCONN_STRONG = 0x0001

CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4

REGCLS_SINGLEUSE         = 0
REGCLS_MULTIPLEUSE       = 1
REGCLS_MULTI_SEPARATE    = 2
REGCLS_SUSPENDED         = 4
REGCLS_SURROGATE         = 8

################################################################

_quit_enabled = 1

class IClassFactory(IUnknown):
    _iid_ = GUID("{00000001-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "CreateInstance", c_int, REFIID, POINTER(DWORD)),
        STDMETHOD(HRESULT, "LockServer", c_int)]

class IExternalConnection(IUnknown):
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "AddConnection", DWORD, DWORD),
        STDMETHOD(HRESULT, "ReleaseConnection", DWORD, DWORD, DWORD)]

################################################################
#
# Algorithm for the server lifetime taken from Don Box: Essential COM
# (German edition, chapter 6.3: Lebensdauer von Server-Prozessen)
#
class ClassFactory(COMObject):
    _com_interfaces_ = [IClassFactory, IExternalConnection]

    def __init__(self, objclass):
        COMObject.__init__(self)
        for itf in self._com_interfaces_:
            self._make_interface_pointer(itf)
        self.objclass = objclass

    def get_interface_pointer(self, interface=IUnknown):
        for iid, itf in self._com_pointers_:
            if interface._iid_ == iid:
                return byref(itf)

    def _register_class(self, regcls=REGCLS_MULTIPLEUSE):
        cookie = c_ulong()
        ole32.CoRegisterClassObject(byref(GUID(self.objclass._reg_clsid_)),
                                    self.get_interface_pointer(),
                                    CLSCTX_LOCAL_SERVER,
                                    regcls,
                                    byref(cookie))
        self.cookie = cookie

    def _revoke_class(self):
        ole32.CoRevokeClassObject(self.cookie)
        del self.cookie

    # IUnknown methods

    def AddRef(self, this):
        return 2

    def Release(self, this):
        return 1

    # IClassFactory methods

    def CreateInstance(self, this, pUnkOuter, riid, ppvObject):
        if pUnkOuter:
            return CLASS_E_NOAGGREGATION
        obj = self.objclass()
        obj._factory = self
        return obj.QueryInterface(None, riid, ppvObject)

    def LockServer(self, this, fLock):
        if fLock:
            ole32.CoAddRefServerProcess()
        else:
            result = ole32.CoReleaseServerProcess()
            if result == 0 and _quit_enabled:
                user32.PostQuitMessage(0)
        return S_OK

    # IExternalConnection methods

    def AddConnection(self, this, extconn, dwReserved):
        if extconn == EXTCONN_STRONG:
            self.LockServer(None, 1)
        return S_OK

    def ReleaseConnection(self, this, extconn, dwReserved, fLastReleaseCloses):
        if extconn == EXTCONN_STRONG:
            self.LockServer(None, 0)
        return S_OK

################################################################

def pump_messages():
    class MSG(Structure):
        _fields_ = [("hwnd", c_int),
                    ("message", c_int),
                    ("wParam", c_int),
                    ("lParam", c_int),
                    ("time", c_int),
                    ("x", c_int),
                    ("y", c_int)]

    msg = MSG()
    while user32.GetMessageA(byref(msg), 0, 0, 0):
        user32.DispatchMessageA(byref(msg))

def localserver(objclass):
    factory = ClassFactory(objclass)
    factory._register_class()
    pump_messages()
    factory._revoke_class()
