from windows import *
from wtl import *
import atl
import form

from ctypes import *

blinkyIcon = Icon("blinky.ico")

class MyForm(form.Form):
    _class_icon_ = blinkyIcon
    _class_icon_sm_ = blinkyIcon
    _class_background_ = 0

    def __init__(self):
        self.menu = Menu()
        self.menuFile = PopupMenu()
        self.menuFile.AppendMenu(MF_STRING, 1000, "&Open...\tCtrl+O")
        self.menuFile.AppendMenu(MF_STRING, 1001, "&Save...\tCtrl+S")
        self.menuFile.AppendMenu(MF_STRING, 1002, "&Save As...")
        self.menuFile.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuFile.AppendMenu(MF_STRING, 1003, "&Exit")
        
        self.menu.AppendMenu(MF_POPUP, self.menuFile, "&File")
        
        form.Form.__init__(self,
                           menu = self.menu,
                           title = "Real Slick Looking Windows Application in 100% Python")      

        self.ctrl = atl.AxWebControl("http://www.python.org",
                                     parent = self)    

        
    def OnSize(self, wParam, lParam):
        cx, cy = LOWORD(lParam), HIWORD(lParam)
        self.ctrl.MoveWindow(0,0,cx,cy,TRUE)
        return (1, 0)

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])

mainForm = MyForm()        
mainForm.ShowWindow()

Run()

print "done"
