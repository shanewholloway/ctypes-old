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
import ctypes
import gdi

class Splitter(Window):
    _class_ws_style_ = WS_CHILD | WS_VISIBLE
    _class_ws_ex_style_ = 0
    _class_background_ = gdi.GetSysColorBrush(gdi.COLOR_ACTIVEBORDER)
    
    def __init__(self, *args, **kwargs):
        self.splitWidth = kwargs.get('splitWidth', 4)
        self.splitPos = kwargs.get('splitPos', 100)
        if kwargs.has_key('splitPos'): del kwargs['splitPos']
        if kwargs.has_key('splitWidth'): del kwargs['splitWidth']
        apply(Window.__init__, (self,) + args, kwargs)

        self.hcursor = LoadCursor(NULL, IDC_SIZEWE)

        brushPat = (c_ushort * 8)()
        for i in range(8):
            brushPat[i] = (0x5555 << (i & 1))

        hbitmap = gdi.CreateBitmap(8, 8, 1, 1, byref(brushPat))
        if hbitmap:
            self.brush = gdi.CreatePatternBrush(hbitmap)
            DeleteObject(hbitmap)
        else:
            self.brush = gdi.CreateHatchBrush(gdi.HS_DIAGCROSS, 0)

        self.views = {}

    def Add(self, index, ctrl):
        #make sure splitter window is at bottom
        self.SetWindowPos(HWND_BOTTOM, 0, 0, 0, 0,
                          SWP_NOACTIVATE|SWP_NOMOVE|SWP_NOREDRAW|SWP_NOSIZE)
        self.views[index] = ctrl
        
    def OnSize(self, event):
        apply(self.Layout, event.size)
        
    def Layout(self, cx, cy):
        wr = self.windowRect
        pt = POINT()        
        pt.x = wr.left
        pt.y = wr.top
        self.GetParent().ScreenToClient(pt)

        #move windows all together
        hdwp = BeginDeferWindowPos(2)
        x, y = int(pt.x), int(pt.y)
        ctrl = self.views[0]
        DeferWindowPos(hdwp, ctrl.handle, NULL, x, y, self.splitPos, cy,
                       SWP_NOACTIVATE | SWP_NOZORDER)
        ctrl = self.views[1]        
        DeferWindowPos(hdwp, ctrl.handle, NULL, self.splitPos + self.splitWidth + x, y,
                        cx - self.splitPos - self.splitWidth, cy, SWP_NOACTIVATE | SWP_NOZORDER)
        EndDeferWindowPos(hdwp)
        

    def OnLeftButtonDown(self, event):        
        x, y = event.position
        self.dragOffset = x - self.splitPos
        if self.IsOverSplitter(x, y):
            self.SetCapture()        
            self.PatBlt(0, x, 0)

    def IsOverSplitter(self, x, y):
        if x >= self.splitPos and x <= self.splitPos + self.splitWidth:
            return 1
        else:
            return 0
        
    def OnLeftButtonUp(self, event):
        if GetCapture() == self.handle:
            x, y = event.position
            x, y = self.Clamp(x, y)
            ReleaseCapture()
            self.PatBlt(0, x, 0)
            rc = self.clientRect
            self.splitPos -= self.dragOffset
            self.Layout(rc.width, rc.height)

    def Clamp(self, x, y):
        if x - self.dragOffset < 10:
            x = 10 + self.dragOffset
        if x > self.clientRect.width - 10 - self.splitWidth + self.dragOffset:
            x = self.clientRect.width - 10 - self.splitWidth + self.dragOffset

        return x, y
    
    def OnMouseMove(self, event):
        if event.wParam & MK_LBUTTON and GetCapture() == self.handle:
            x, y = event.position
            x, y = self.Clamp(x, y)        
            self.PatBlt(self.splitPos, x, 1)
            
    def PatBlt(self, oldPos, newPos, eraseOld):
        if oldPos == newPos: return
        
        hdc = self.GetDCEx(NULL, DCX_PARENTCLIP)
        hbr = gdi.SelectObject(hdc, self.brush)

        if eraseOld:
            gdi.PatBlt(hdc, oldPos - self.dragOffset, 0, self.splitWidth, self.clientRect.height,
                       gdi.PATINVERT)
            
        gdi.PatBlt(hdc, newPos - self.dragOffset, 0, self.splitWidth, self.clientRect.height,
                   gdi.PATINVERT)

        gdi.SelectObject(hdc, hbr)
        self.ReleaseDC(hdc)

        self.splitPos = newPos
        

    def OnSetCursor(self, event):
        x, y = GET_XY_LPARAM(GetMessagePos())
        pt = POINT(x, y)
        self.ScreenToClient(pt)
        if self.IsOverSplitter(pt.x, pt.y):
            SetCursor(self.hcursor)

    def OnCaptureChanged(self, event):
        #TODO?
        #self.PatBlt(0, self.splitPos, 0)
        pass
        
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         MSG_HANDLER(WM_LBUTTONDOWN, OnLeftButtonDown),
                         MSG_HANDLER(WM_LBUTTONUP, OnLeftButtonUp),
                         MSG_HANDLER(WM_MOUSEMOVE, OnMouseMove),
                         MSG_HANDLER(WM_SETCURSOR, OnSetCursor),
                         MSG_HANDLER(WM_CAPTURECHANGED, OnCaptureChanged)])
        
    

