from ctypes.com import IUnknown, PIUnknown, COMObject, ole32, \
     GUID, HRESULT, STDMETHOD, REFIID
from ctypes.com.automation import IDispatch, oleaut32
from ctypes import *

user32 = windll.user32
kernel32 = windll.kernel32
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

# Hm. We cannot redirect sys.stderr/sys.stdout in the inproc case,
# If the process is Python, the user would be pissed off if we did.
class _Logger(object):
    # Redirect standard output and standard error to
    # win32 Debug Messages. Output can be viewed for example
    # in DebugView from www.sysinternals.com
    _installed = 0
    _text = ""
    def write(self, text):
        self._text += str(text)
        if "\n" in self._text:
            kernel32.OutputDebugStringA(self._text)
            self._text = ""

    def install(cls):
        if cls._installed:
            return
        import sys
        sys.stdout = sys.stderr = cls()
        cls._installed = 1
    install = classmethod(install)

    def isatty(self):
        return 0

def inproc_find_class(clsid):
    import _winreg
##    print str(clsid)
    key = _winreg.OpenKey(_winreg.HKEY_CLASSES_ROOT, "CLSID\\%s" % clsid)
    import sys
    try:
        pathdir = _winreg.QueryValue(key, "PythonPath")
    except WindowsError:
        pass
    else:
        if not pathdir in sys.path:
            sys.path.insert(0, pathdir)
##            print "appended %s to sys.path" % pathdir
##            print "SYS.PATH", sys.path
    pythonclass = _winreg.QueryValue(key, "PythonClass")
##    print pythonclass
    parts = pythonclass.split(".")
    modname = ".".join(parts[:-1])
    classname = parts[-1]
    __import__(modname)
    mod = sys.modules[modname]
##    print "imported", mod

    # It was a nice idea to 'reload' the module, so that during
    # debugging we would always run uptodate versions of the code.
    # The problem is that super(type, obj) sometimes doesn't work
    # correctly anymore because 'obj' would not be an instance of
    # 'type' anymore.
    #
    # So, unfortuately, we cannot use this.
##    if __debug__:
##        reload(mod)

##    print "returning", getattr(mod, classname)
    return getattr(mod, classname)

# Fake implementation, with hardcoded names
def inproc_find_class(clsid):
    import sys
    pathdir = r"c:\sf\ctypes_head\win32\com\samples\server"
    if not pathdir in sys.path:
        sys.path.insert(0, pathdir)
    classname = "SumObject"
    modname = "sum"
    __import__(modname)
    mod = sys.modules[modname]
    return getattr(mod, classname)

def DllGetClassObject(rclsid, riid, ppv):
    # This function is called by C code, and receives C integers as
    # parameters. rcslid is a pointer to the CLSID for the coclass we
    # want to be created, riid is a pointer to the requested
    # interface.
    _Logger.install()

    iid = GUID.from_address(riid)
    clsid = GUID.from_address(rclsid)
    p = PIUnknown.from_address(ppv)

    print "\tDllGetClassObject called with", clsid, iid
    # Use the clsid to find additional info in the registry.
    cls = inproc_find_class(clsid)
    # XXX Hm, does inproc_findclass return None, or raise an Exception?
    if not cls:
        return CLASS_E_CLASSNOTAVAILABLE
    global _active_objects
    factory = ClassFactory(cls)
    _active_objects.append(factory)
    obj = pointer(factory._com_pointers_[0][1])
    # obj is a pointer to the class factory's IClassFactory interface.
    return obj.QueryInterface(byref(iid), byref(p))

_active_objects = []

S_FALSE = 0x00000001
S_OK = 0x00000000

def DllCanUnloadNow():
    # XXX TODO: Read about inproc server refcounting in Don Box
    return S_FALSE
    _Logger.install()
    if _active_objects:
        print "* DllCanUnloadNow -> S_FALSE", _active_objects
        return S_FALSE
    else:
        print "* DllCanUnloadNow -> S_OK"
        return S_OK
    # Hm Call ole32.CoUnitialize here?


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
        print "AddRef", self
        return 2

    def Release(self, this):
        print "Release", self
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
    from ctypes.wintypes import MSG
    msg = MSG()
    while user32.GetMessageA(byref(msg), 0, 0, 0):
        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageA(byref(msg))

def localserver(objclass):
    factory = ClassFactory(objclass)
    factory._register_class()
    pump_messages()
    factory._revoke_class()

def UseCommandLine(cls):
    import sys
    from ctypes.com.w_getopt import w_getopt
    from ctypes.com.register import register, unregister
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
