from windows import *
from wtl import *
import gdi
import form

class Form(form.Form):
    _class_icon_ = Icon("blinky.ico")
    _class_icon_sm_ = _class_icon_
    _class_background_ = 0 #prevents windows from redrawing background, prevent flicker
    _class_style_ = CS_HREDRAW | CS_VREDRAW#make windows invalidate window on resize
    
    def __init__(self):
        form.Form.__init__(self,
                           title = "Real Slick Looking Windows Application in 100% Python")      

        try:
            self.bitmap = Bitmap("test.bmp")
        except:
            print "put a bitmap file 'test.bmp' in the current directory"
            import os
            os._exit(-1)
            
        self.bitmapdc = gdi.CreateCompatibleDC(NULL)
        gdi.SelectObject(self.bitmapdc, self.bitmap.handle)
        
    def OnPaint(self, event):
        ps = PAINTSTRUCT()
        hdc = self.BeginPaint(ps)
        
        rc = self.GetClientRect()

        gdi.StretchBlt(hdc, 0, 0, rc.right , rc.bottom,
                       self.bitmapdc, 0, 0, self.bitmap.width, self.bitmap.height,
                       SRCCOPY)
        
        self.EndPaint(ps)

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_PAINT, OnPaint),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])
    

w = Form()        
w.ShowWindow()
w.UpdateWindow()

Run()
print "done"
