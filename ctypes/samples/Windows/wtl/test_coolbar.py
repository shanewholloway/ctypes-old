from windows import *
from wtl import *
import atl
import comctl
import gdi
import notebook
import form
import splitter
import tree
import list
import coolbar

comctl.InitCommonControls(comctl.ICC_LISTVIEW_CLASSES | comctl.ICC_COOL_CLASSES |\
                          comctl.ICC_USEREX_CLASSES)

ID_NEW = 1001
ID_EXIT = 1002

class Form(form.Form):
    _class_icon_ = Icon("COW.ICO")
    _class_icon_sm_ = _class_icon_
    _class_background_ = 0
    _class_accels_ = [(FCONTROL|FVIRTKEY, ord("N"), ID_NEW)]
    _class_form_exit_ = form.EXIT_ONLASTDESTROY
    _class_form_status_msgs_ = {ID_NEW: "Creates a new window."}
    
    def __init__(self):
        self.enableLayout = 0 #supress layout due to rebar notfications during construction
        self.CreateMenu()
        
        form.Form.__init__(self,
                           title = "Supervaca al Rescate!")      

        self.coolBar = coolbar.CoolBar(parent = self)

        self.commandBar = coolbar.CommandBar(parent = self.coolBar)
        self.commandBar.AttachMenu(self.menu)
        
        self.addressBar = comctl.ComboBox(parent = self.coolBar)

        self.coolBar.SetRedraw(0)
        self.coolBar.AddSimpleRebarBandCtrl(self.commandBar)
        self.coolBar.AddSimpleRebarBandCtrl(self.addressBar, bNewRow = TRUE)
        self.coolBar.SetRedraw(1)
        
        self.list = list.List(parent = self,
                              orExStyle = WS_EX_CLIENTEDGE)
       
        self.list.InsertColumns([("blaat", 100), ("col2", 150)])
        self.list.SetRedraw(0)
        for i in range(100):
            self.list.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])
        self.list.SetRedraw(1)
    

        self.statusBar = comctl.StatusBar(parent = self)

        self.enableLayout = 1
        
    def CreateMenu(self):
        self.menu = Menu()

        self.menuFilePopup = PopupMenu()
        self.menuFilePopup.AppendMenu(MF_STRING, 1018, "&Blaat...\tCtrl+O")
        self.menuFilePopup.AppendMenu(MF_STRING, 1013, "&Piet...\tCtrl+S")
        
        self.menuFile = PopupMenu()
        self.menuFile.AppendMenu(MF_POPUP, self.menuFilePopup, "&New")
        self.menuFile.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuFile.AppendMenu(MF_STRING, 1008, "&Open...\tCtrl+O")
        self.menuFile.AppendMenu(MF_STRING, 1003, "&Save...\tCtrl+S")
        self.menuFile.AppendMenu(MF_STRING, 1004, "&Save As...")
        self.menuFile.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuFile.AppendMenu(MF_STRING, ID_EXIT, "&Exit")
        self.menu.AppendMenu(MF_POPUP, self.menuFile, "&File")

        self.menuEdit = PopupMenu()
        self.menuEdit.AppendMenu(MF_STRING, 3004, "&Undo\bCtrl-Z")
        self.menuEdit.AppendMenu(MF_STRING, 3005, "&Redo")
        self.menuEdit.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuEdit.AppendMenu(MF_STRING, 3006, "&Copy")
        self.menuEdit.AppendMenu(MF_STRING, 3007, "&Paste")
        self.menuEdit.AppendMenu(MF_STRING, 3008, "&Cut")
        self.menu.AppendMenu(MF_POPUP, self.menuEdit, "&Edit")

    def DoLayout(self, cx, cy):
        if not self.enableLayout: return
        statusBarHeight = self.statusBar.windowRect.height
        coolBarHeight = self.coolBar.windowRect.height
                
        hdwp = BeginDeferWindowPos(3)
        DeferWindowPos(hdwp, self.coolBar.handle, NULL, 0, 0,
                       cx, coolBarHeight, SWP_NOACTIVATE | SWP_NOZORDER)
        DeferWindowPos(hdwp, self.statusBar.handle, NULL, 0, cy - statusBarHeight,
                       cx, statusBarHeight, SWP_NOACTIVATE | SWP_NOZORDER)
        DeferWindowPos(hdwp, self.list.handle, NULL, 0, coolBarHeight,
                       cx, cy - statusBarHeight - coolBarHeight, SWP_NOACTIVATE | SWP_NOZORDER)
        EndDeferWindowPos(hdwp)

        self.coolBar.Invalidate()
        
    def OnNew(self, event):
        form = Form()
        form.ShowWindow()

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE,
                                     lambda self,
                                     event: apply(self.DoLayout, event.size)),       
                         CMD_HANDLER(ID_NEW, OnNew),
                         CMD_HANDLER(ID_EXIT,
                                     lambda self, event: self.DestroyWindow()),
                         NTF_HANDLER(comctl.RBN_HEIGHTCHANGE,
                                     lambda self,
                                     event: apply(self.DoLayout, self.clientRect.size)),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])


mainForm = Form()
mainForm.ShowWindow()
Run()

print "done"
