import _winreg, sys
from ctypes import *
from ctypes.wintypes import DWORD
from ctypes.com import IUnknown, PIUnknown, COMObject, ole32, \
     GUID, HRESULT, STDMETHOD, REFIID, CLSCTX_INPROC_SERVER, CLSCTX_LOCAL_SERVER
from ctypes.com.hresult import *
from ctypes.com.w_getopt import w_getopt
from ctypes.com.register import register, unregister

user32 = windll.user32
kernel32 = windll.kernel32

EXTCONN_STRONG = 0x0001

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

def dprint(*args):
    parts = [str(arg) for arg in args] + ["\n"]
    kernel32.OutputDebugStringA(" ".join(parts))
##    print " ".join(parts)

class Logger:
    def write(self, msg):
        kernel32.OutputDebugStringA(msg)

    def isatty(self):
        return False

    def install(cls):
        import sys
        sys.stdout = sys.stderr = cls()
    install = classmethod(install)

def inproc_find_class(clsid):
    key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, "CLSID\\%s\\InprocServer32" % clsid)
    try:
        pathdir = _winreg.QueryValueEx(key, "PythonPath")[0]
    except WindowsError:
        pass
    else:
        if not pathdir in sys.path:
            sys.path.insert(0, str(pathdir))
##            dprint("appended %s to sys.path" % pathdir)
##            dprint("SYS.PATH", sys.path)
    pythonclass = _winreg.QueryValueEx(key, "PythonClass")[0]
    parts = pythonclass.split(".")
    modname = ".".join(parts[:-1])
    classname = parts[-1]
    __import__(modname)
    mod = sys.modules[modname]
##    dprint("imported", mod)

    # It was a nice idea to 'reload' the module, so that during
    # debugging we would always run uptodate versions of the code.
    # The problem is that super(type, obj) sometimes doesn't work
    # correctly anymore because 'obj' would not be an instance of
    # 'type' anymore.
    #
    # So, unfortuately, we cannot use this.
##    if __debug__:
##        reload(mod)

##    dprint("returning", getattr(mod, classname))
    return getattr(mod, classname)

def DllGetClassObject(rclsid, riid, ppv):
    Logger.install()

    print "DllGetClassObject %s" % ((rclsid, riid, ppv),)

    # This function is called by C code, and receives C integers as
    # parameters. rcslid is a pointer to the CLSID for the coclass we
    # want to be created, riid is a pointer to the requested
    # interface.
    iid = GUID.from_address(riid)
    clsid = GUID.from_address(rclsid)
    p = POINTER(IUnknown).from_address(ppv)

    # Use the clsid to find additional info in the registry.
    cls = inproc_find_class(clsid)
##    dprint("DllGetClassObject", clsid, cls)

    # XXX Hm, does inproc_findclass return None, or raise an Exception?
    if not cls:
        return CLASS_E_CLASSNOTAVAILABLE
    factory = InprocClassFactory(cls)
    _active_objects.append(factory)

    obj = pointer(factory._com_pointers_[0][1])
    obj.AddRef()
    
    # XXX Why is this one needed?
    obj.AddRef()

    # QueryInterface, if successful, increments the refcount itself.
    return obj.QueryInterface(byref(iid), byref(p))

_active_objects = []
g_locks = 0

def DllCanUnloadNow():
    # XXX TODO: Read about inproc server refcounting in Don Box
    if g_locks:
        dprint("* DllCanUnloadNow -> S_FALSE", _active_objects)
        return S_FALSE
    else:
        dprint("* DllCanUnloadNow -> S_OK")
        return S_OK
    # Hm Call ole32.CoUnitialize here?


################################################################
class _ClassFactory(COMObject):
    _com_interfaces_ = [IClassFactory]

    def __init__(self, objclass):
        COMObject.__init__(self)
        for itf in self._com_interfaces_:
            self._make_interface_pointer(itf)
        self.objclass = objclass

    # IClassFactory methods

    def CreateInstance(self, this, pUnkOuter, riid, ppvObject):
        if pUnkOuter:
            return CLASS_E_NOAGGREGATION
        obj = self.objclass()
        obj._factory = self
        _active_objects.append(obj)
        return obj.QueryInterface(None, riid, ppvObject)

################################################################
class InprocClassFactory(_ClassFactory):

    def AddRef(self, this):
        self._refcnt += 1
##        dprint("AddRef", self, self._refcnt)
##?##        self._factory.LockServer(None, 1)
        return self._refcnt

    def Release(self, this):
        self._refcnt -= 1
##        dprint("Release", self, self._refcnt)
##?##        self._factory.LockServer(None, 0)
        return self._refcnt

    def LockServer(self, this, fLock):
        global g_locks
        if fLock:
            g_locks += 1
        else:
            g_locks -= 1
        dprint("LockServer", fLock, g_locks)
            
################################################################
#
# Algorithm for the server lifetime taken from Don Box: Essential COM
# (German edition, chapter 6.3: Lebensdauer von Server-Prozessen)
#
class LocalServerClassFactory(_ClassFactory):
    _com_interfaces_ = [IClassFactory, IExternalConnection]

    def get_interface_pointer(self, interface=IUnknown):
        # XXX Should this be reworked to return itf instead of byref(itf)?
        # Or should it return pointer(itf)?
        for iid, itf in self._com_pointers_:
            if interface._iid_ == iid:
                return byref(itf)
        # and shouldn't we raise an exception here?

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
    from ctypes.wintypes import MSG
    msg = MSG()
    while user32.GetMessageA(byref(msg), 0, 0, 0):
        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageA(byref(msg))

def localserver(objclass):
    factory = LocalServerClassFactory(objclass)
    factory._register_class()
    pump_messages()
    factory._revoke_class()

def UseCommandLine(cls):
    opts, args = w_getopt(sys.argv[1:], "regserver unregserver embedding".split())
    if not opts:
        return 0 # nothing for us to do

    for option, value in opts:
        if option == "regserver":
            register(cls)
        elif option == "unregserver":
            unregister(cls)
        elif option == "embedding":
            localserver(cls)

    return 1 # we have done something
