from ctypes import windll, byref, c_int
from ctypes.wintypes import DWORD, MSG

from ctypes.com import CreateInstance
from ctypes.com.automation import VARIANT
from ctypes.com.connectionpoints import dispinterface_EventReceiver, GetConnectionPoint

from ie6_gen import InternetExplorer, IWebBrowser2, DWebBrowserEvents2

# To receive events, we have to run a message loop:
def pump_messages():
    user32 = windll.user32
    msg = MSG()
    while user32.GetMessageA(byref(msg), None, 0, 0):
        user32.TranslateMessage(byref(msg))
        user32.DispatchMessageA(byref(msg))

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
# We have to at least implement the OnQuit method which is called when
# the Browser is closed, we use it to post q QuitMessage to ourself so
# that the message loop terminates.

class DWebBrowserEvents2Impl(dispinterface_EventReceiver):
    _com_interfaces_ = [DWebBrowserEvents2]

    # The base class will call all methods we implement here,
    # and simply print the method name with the arguments
    # for unimplemented methods.
    def OnQuit(self, this, *args):
        print "OnQuit", self, this, args
        windll.user32.PostQuitMessage(0)

    def BeforeNavigate2(self, this, pDisp, URL, Flags, TargetFrameName,
                        PostData, Headers, Cancel):
        print "BeforeNavigate2", pDisp, URL, Flags, \
              TargetFrameName, Headers, Cancel
##        if URL.value == "http://www.python.org/download/":
##            Cancel.value = True
##            print "CANCEL!!!"

    def NavigateComplete2(self, this, pDisp, URL):
        print "NavigateComplete2", URL

    def FileDownload(self, this, spam, cancel):
        print "FileDownload", this, spam, cancel
##        cancel.value = True
##        print "FileDownload canceled", cancel

################################################################

# Start InternetExplorer as ActiveX object
browser = CreateInstance(InternetExplorer)

# We can now call methods on it
#
# Note that readtlb *can* create Python properties from COM properties,
# but I don't like the code which is generated, it is too verbose IMO.
# So this is disabled by default, to enable it see the readtlb.py script.
browser._put_Visible(1)
v = c_int()
browser._get_Visible(byref(v))
print "Is visible?", hex(v.value)

# We are interested in events, so create the event receiver instance...
events = DWebBrowserEvents2Impl()
# ...and connect it to the browser (the event source).
info = events.connect(browser)

# Call the Navigate method. We have to supply empty values for all arguments:
v = VARIANT()
browser.Navigate("http://www.python.org/",
                 byref(v), byref(v), byref(v), byref(v))

# To receive event, we have to run a message loop.
# The messageloop is terminated by posting a quit message,
# which is done in the handler for the OnQuit event.
pump_messages()

# To be nice, we clean up.
events.disconnect(info)
print "disconnected"

