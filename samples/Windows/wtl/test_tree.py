from windows import *
from wtl import *
import tree
import form
import comctl
import gdi

from ctypes import *

blinkyIcon = Icon("blinky.ico")

ID_EXIT = 1001

class Tree(tree.Tree):
    def __init__(self, *args, **kwargs):
        apply(tree.Tree.__init__, (self,) + args, kwargs)

        self.iml = comctl.ImageList(16, 16, ILC_COLOR32 | ILC_MASK, 0, 32)
        self.iml.AddIconsFromModule("shell32.dll", 16, 16, LR_LOADMAP3DCOLORS)
        self.iml.SetBkColor(gdi.CLR_NONE)
        self.SetImageList(self.iml)

        self.SetRedraw(0)
        hRoot = self.InsertItem(comctl.TVI_ROOT, comctl.TVI_ROOT, "A root", 17, 17)
        for i in range(100):
            hChild = self.InsertItem(hRoot, comctl.TVI_LAST, "A child %d" % i, 3, 4)
        self.SetRedraw(1)

    def OnItemExpanding(self, event):
        print "item expanding"

    def OnSelectionChanged(self, event):
        print "on sel changed"
        nmtv = comctl.NMTREEVIEW.from_address(int(event.lParam))
        
    _msg_map_ = MSG_MAP([NTF_HANDLER(comctl.TVN_ITEMEXPANDING, OnItemExpanding),
                         NTF_HANDLER(comctl.TVN_SELCHANGED, OnSelectionChanged)])

class MyForm(form.Form):
    _class_icon_ = blinkyIcon
    _class_icon_sm_ = blinkyIcon
    _class_background_ = 0

    def __init__(self):
        self.menu = Menu()
        self.menuFile = PopupMenu()
        self.menuFile.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuFile.AppendMenu(MF_STRING, ID_EXIT, "&Exit")
        self.menu.AppendMenu(MF_POPUP, self.menuFile, "&File")
        
        form.Form.__init__(self,
                           menu = self.menu,
                           title = "Tree test")      

        self.ctrl = Tree(parent = self, orExStyle = WS_EX_CLIENTEDGE)
    
        
    def OnSize(self, event):
        cx, cy = event.size
        self.ctrl.MoveWindow(0, 0, cx, cy, TRUE)
        

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         CMD_HANDLER(ID_EXIT, lambda self, event: self.DestroyWindow()),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])

        
mainForm = MyForm()        
mainForm.ShowWindow()
Run()

print "done"
