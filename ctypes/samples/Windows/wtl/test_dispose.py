from windows import *
from wtl import *
import form

blinkyIcon = Icon("blinky.ico")

ID_NEW = 1001
ID_EXIT = 1002

class MyForm(form.Form):
    _class_icon_ = blinkyIcon
    _class_icon_sm_ = blinkyIcon
    _class_form_exit_ = form.EXIT_ONLASTDESTROY
    _class_accels_ = [(FCONTROL|FVIRTKEY, ord("N"), ID_NEW)]
                      

    def __init__(self):
        self.menu = Menu()
        self.menuFile = PopupMenu()
        self.menuFile.AppendMenu(MF_STRING, ID_NEW, "&New\bCtrl+N")
        self.menuFile.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuFile.AppendMenu(MF_STRING, ID_EXIT, "&Exit")
        self.menu.AppendMenu(MF_POPUP, self.menuFile, "&File")
        
        form.Form.__init__(self, menu = self.menu, title = "Python")      

    def OnNew(self, event):
        newForm = MyForm()
        newForm.ShowWindow()

    def OnExit(self, event):
        self.DestroyWindow()
        
    _msg_map_ = MSG_MAP([CMD_HANDLER(ID_NEW, OnNew),
                         CMD_HANDLER(ID_EXIT, OnExit),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])

mainForm = MyForm()        
mainForm.ShowWindow()
Run()


