## 	   Copyright (c) 2003 Henk Punt

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:

## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
## LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

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
                    lpmsg = byref(msg)
                    if self.pOle.TranslateAccelerator(lpmsg) == 0:
                        #translation has happened
                        return 1
                    

        
    
