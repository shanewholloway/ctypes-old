from ctypes.com import ole32, IUnknown, GUID, PIUnknown, REFCLSID, REFIID
from ctypes.com.connectionpoints import IConnectionPointContainer, IConnectionPoint,\
     GetConnectionPoint
from ctypes.com.automation import BSTR, VARIANT
from ctypes import byref, c_long, c_ulong, c_double, oledll, POINTER, pointer, c_voidp
from ctypes import windll
user32 = windll.user32

from ie6_gen import InternetExplorer, IWebBrowser2, DWebBrowserEvents2

oleaut32 = oledll.oleaut32

# XXX
CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4
DWORD = c_ulong

################################################################

ole32.CoInitialize(None)
ole32.CoCreateInstance.argtypes = REFCLSID, c_voidp, DWORD, REFIID, POINTER(PIUnknown)

def CreateInstance(coclass, interface=None,
                   clsctx = CLSCTX_INPROC_SERVER|CLSCTX_LOCAL_SERVER):
    if interface is None:
        interface = coclass._com_interfaces_[0]
    p = pointer(interface())
    clsid = GUID(coclass._regclsid_)
    ole32.CoCreateInstance(byref(clsid),
                           0,
                           clsctx,
                           byref(interface._iid_),
                           byref(p))
    return p

################################################################

from ctypes.com.connectionpoints import dispinterface_EventReceiver

class DWebBrowserEvents2Impl(dispinterface_EventReceiver):
    _com_interfaces_ = [DWebBrowserEvents2]

    # The base class will call all methods we implement here,
    # and simply print the method name with the arguments
    # for unimplemented methods.
    def OnQuit(self, *args):
        print "OnQuit", args
        user32.PostQuitMessage(0)

################################################################

browser = CreateInstance(InternetExplorer)
browser._put_Visible(1)

cp = GetConnectionPoint(browser, DWebBrowserEvents2)

comobj = DWebBrowserEvents2Impl()
pevents = comobj._com_pointers_[0][1]

cookie = DWORD()
cp.Advise(byref(pevents), byref(cookie))

v = VARIANT()
browser.Navigate("http://www.python.org/",
                 byref(v), byref(v), byref(v), byref(v))

from ctypes.wintypes import MSG
msg = MSG()
while user32.GetMessageA(byref(msg), None, 0, 0):
    user32.TranslateMessage(byref(msg))
    user32.DispatchMessageA(byref(msg))
