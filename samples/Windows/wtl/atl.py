from windows import *
from ctypes import *
import wtl

AtlAxWinInit = windll.atl.AtlAxWinInit
AtlAxGetControl = windll.atl.AtlAxGetControl

class AxWindow(wtl.Window):
    _class_ = "AtlAxWin"
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN
    
    def __init__(self, ctrlId, *args, **kwargs):
        AtlAxWinInit()
        kwargs['title'] = ctrlId
        apply(wtl.Window.__init__, (self,) + args, kwargs)        

import COM

class AxWebControl(AxWindow):
    _class_ws_style_ = AxWindow._class_ws_style_ | WS_HSCROLL | WS_VSCROLL

    def __init__(self, url, *args, **kwargs):
        kwargs['ctrlId'] = url
        apply(AxWindow.__init__, (self,) + args, kwargs)

        pUnk = COM.IUnknownPointer()
        AtlAxGetControl(self.handle, byref(pUnk))
        #pDisp = COM.IDispatchPointer()
        #pUnk.QueryInterface(byref(COM.IDispatch._iid_),
        #                          byref(pDisp))
        #disp = COM.Dispatch(None, pDisp)
        #disp.Navigate("http://www.microsoft.com")

        pOle = COM.IOleInPlaceActiveObjectPointer()
        pUnk.QueryInterface(byref(COM.IOleInPlaceActiveObject._iid_),
                            byref(pOle))
        self.pOle = pOle

        #global msg loop filter needed, see PreTranslateMessage
        wtl.GetMessageLoop().AddFilter(self) #TODO remove on destroy
        
    #filter needed to make 'del' and other accel keys work
    #within IE control. @see http://www.microsoft.com/mind/0499/faq/faq0499.asp
    def PreTranslateMessage(self, msg):
        #here any keyboard message from the app passes:
        if msg.message >= WM_KEYFIRST and  msg.message <= WM_KEYLAST:
            #now we see if the control which sends these msgs is a child of
            #this axwindow (for instance input control embedded in html page)
            parent = msg.hWnd
            while parent:
                parent = GetParent(int(parent))
                if parent == self.handle:
                    #yes its a child of mine
                    lpmsg = pointer(msg)
                    if self.pOle.TranslateAccelerator(lpmsg) == 0:
                        #translation has happened
                        return 1
                    

        
    
