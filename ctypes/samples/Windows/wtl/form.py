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
from wtl import *

EXIT_NONE = 0
EXIT_ONDESTROY = 1
EXIT_ONLASTDESTROY = 2

class Form(Window):
    """A class representing an applications main window. This class
    supports accelerators, automatic closing of the application with
    simple window management
    For status bar support make sure you have a statusBar property in
    your derived Form and provide _class_form_status_msgs_ to enable
    help msgs on the statusbar
    """
    
    _class_ws_style = WS_OVERLAPPEDWINDOW | WS_VISIBLE | WS_OVERLAPPED
    _class_ws_ex_style_ = WS_EX_LEFT | WS_EX_LTRREADING | WS_EX_RIGHTSCROLLBAR | \
                          WS_EX_WINDOWEDGE | WS_EX_APPWINDOW

    _class_accels_ = []
    _haccel_ = 0

    _class_form_exit_ = EXIT_ONDESTROY
    _class_form_count_ = 0
    _class_form_status_msgs_ = {} #maps command_id's to status bar msgs
    
    def __init__(self, *args, **kwargs):
        apply(Window.__init__, (self,) + args, kwargs)        
        self.CreateAccels()
        GetMessageLoop().AddFilter(self)
        Form._class_form_count_ += 1
        
    def CreateAccels(self):
        """Create accelerator table from _class_accels_"""
        if self._class_accels_ and not Form._haccel_:
            accels = (ACCEL * len(self._class_accels_))()
            for i in range(len(self._class_accels_)):
                accels[i].fVirt = self._class_accels_[i][0]
                accels[i].key   = self._class_accels_[i][1]
                accels[i].cmd   = self._class_accels_[i][2]
            Form._haccel_ = CreateAcceleratorTable(byref(accels), len(self._class_accels_))
        
    def PreTranslateMessage(self, msg):
        if Form._haccel_:
            return TranslateAccelerator(self.handle, Form._haccel_, byref(msg))
        else:
            return 0
    
    def OnDestroy(self, event):
        Form._class_form_count_ -= 1
        if self._class_form_exit_ == EXIT_ONDESTROY:
            PostQuitMessage(0)
        elif self._class_form_exit_ == EXIT_ONLASTDESTROY and \
             self._class_form_count_ == 0:
            PostQuitMessage(0)

        GetMessageLoop().RemoveFilter(self)
        #TODO dispose Accel Table

    def OnMenuSelect(self, event):
        """displays short help msg for menu command on statusbar"""
        if not hasattr(self, 'statusBar'): return
        
        wFlags = HIWORD(event.wParam)
        if wFlags == -1 and event.lParam == 0:
            self.statusBar.Simple(0)
        else:
            txt = self._class_form_status_msgs_.get(LOWORD(event.wParam), "")
            self.statusBar.Simple(1)
            self.statusBar.SetText(txt)
            
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_DESTROY, OnDestroy),
                         MSG_HANDLER(WM_MENUSELECT, OnMenuSelect)])
        


    
    

