from ctypes import windll, byref, c_int
from ctypes.wintypes import DWORD, MSG

from ctypes.com import CreateInstance
from ctypes.com.automation import VARIANT
from ctypes.com.connectionpoints import dispinterface_EventReceiver, GetConnectionPoint

from ie6_gen import InternetExplorer, IWebBrowser2, DWebBrowserEvents2

################################################################
#
# dispinterface_EventReceiver is a base class which implements a
# dispinterface. Subclasses must have the _com_interfaces_ attribute,
# and the first item on this list must be a dispinterface class.  The
# dispinterface metaclass builds a _dispmap_ attribute from the
# _methods_ list, which is a dictionary mapping dispid integers to
# method names.
#
# Finally the dispinterface_EventReceiver class has an Invoke method,
# called by COM, which converts the argument array passed by COM to a
# tuple of Python values, dynamically looks up the method to call, and
# calls this method.  If no method is found, a warning is printed
# containing the method name and the argument tuple.
#
# The only method we implement here is the OnQuit method which is
# called when the Browser is closed, we use it to post q QuitMessage
# to ourself so that the message loop terminates.

class DWebBrowserEvents2Impl(dispinterface_EventReceiver):
    _com_interfaces_ = [DWebBrowserEvents2]

    # The base class will call all methods we implement here,
    # and simply print the method name with the arguments
    # for unimplemented methods.
    def OnQuit(self, this, *args):
        print "OnQuit", self, args
        windll.user32.PostQuitMessage(0)

################################################################

# Start InternetExplorer as ActiveX object
browser = CreateInstance(InternetExplorer)
# We can now call methods on it
browser._put_Visible(1)
v = c_int()
browser._get_Visible(byref(v))
print "Is visible?", hex(v.value)

# But we also want to receive events from it via the
# DWebBrowserEvents2 interface.

# Get a connection point, this is a pointer to a IConnectionPoint
# interface.
cp = GetConnectionPoint(browser, DWebBrowserEvents2)

# We have to implement the COM object which will receive the events,
# and retrieve a pointer to the DWebBrowserEvents2 interface:
comobj = DWebBrowserEvents2Impl()
# _com_pointers_ is a sequence of (guid, interface_pointer) pairs.
# Get the interface_pointer to the first (default) interface.
pevents = comobj._com_pointers_[0][1]

# We call the Advise method on the IConnectionPoint interface, we supply
# a pointer to a DWORD where a value will be stored which is used to identify
# the connection:
cookie = DWORD()
cp.Advise(byref(pevents), byref(cookie))
# The connection is now established.

# Call the Navigate method. We have to supply empty values for all arguments:
v = VARIANT()
browser.Navigate("http://www.python.org/",
                 byref(v), byref(v), byref(v), byref(v))

# To receive events, we have to run a message loop:
def pump_messages():
    user32 = windll.user32
    msg = MSG()
    while user32.GetMessageA(byref(msg), None, 0, 0):
        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageA(byref(msg))

pump_messages()
