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

comctl.InitCommonControls(comctl.ICC_LISTVIEW_CLASSES | comctl.ICC_COOL_CLASSES |\
                          comctl.ICC_USEREX_CLASSES)

ID_NEW = 1001
ID_EXIT = 1002

class Form(form.Form):
    _class_icon_ = Icon("blinky.ico")
    _class_icon_sm_ = _class_icon_
    _class_background_ = 0
    _class_accels_ = [(FCONTROL|FVIRTKEY, ord("O"), 8003),
                      (FCONTROL|FVIRTKEY, ord("N"), ID_NEW)]
    _class_form_exit_ = form.EXIT_ONLASTDESTROY

    def __init__(self):
        self.CreateMenu()
        
        form.Form.__init__(self,
                           menu = self.menu,
                           title = "Real Slick Looking Windows Application in 100% Python")      

        self.ctrl = notebook.NoteBook(parent = self,
                                      orExStyle = WS_EX_CLIENTEDGE)
        
        self.ie = atl.AxWebControl("http://www.python.org",
                                   parent = self.ctrl,
                                   orExStyle = WS_EX_CLIENTEDGE)
        
        self.list = list.List(parent = self.ctrl,
                              orExStyle = WS_EX_CLIENTEDGE)
        
        self.list.InsertColumns([("blaat", 100), ("col2", 150)])
        for i in range(100):
            self.list.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])
    
        
        self.ctrl.AddTab(0, "blaat1", self.ie)
        self.ctrl.AddTab(1, "blaat2", self.list)

        

        self.statusbar = comctl.StatusBar(parent = self)

                
        self.tree = tree.Tree(parent = self,
                              orExStyle = WS_EX_CLIENTEDGE)
        
        hRoot = self.tree.InsertItem(TVI_ROOT, TVI_ROOT, "A root")
        for i in range(100):
            hChild = self.tree.InsertItem(hRoot, TVI_LAST, "A child %d" % i)

        self.iml = comctl.ImageList(16, 16, ILC_COLOR32, 0, 2)
        self.bm = Bitmap("fldr_closed.bmp")
        self.iml.AddMasked(self.bm, 0)
        self.tree.SetImageList(self.iml)

        self.splitter = splitter.Splitter(parent = self, splitPos = 150)
        self.splitter.Add(0, self.tree)
        self.splitter.Add(1, self.ctrl)

    def CreateMenu(self):
        self.menu = Menu()
    
        self.menuFile = PopupMenu()
        self.menuFile.AppendMenu(MF_STRING, ID_NEW, "&New\tCtrl+N")
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

    def OnSize(self, wParam, lParam):
        cx, cy = LOWORD(lParam), HIWORD(lParam)

        statusBarHeight = self.statusbar.windowRect.height
        
        hdwp = BeginDeferWindowPos(2)
        DeferWindowPos(hdwp, self.statusbar.handle, NULL, 0, cy - statusBarHeight,
                       cx, statusBarHeight, SWP_NOACTIVATE | SWP_NOZORDER)
        DeferWindowPos(hdwp, self.splitter.handle, NULL, 0, 0,
                       cx, cy - statusBarHeight, SWP_NOACTIVATE | SWP_NOZORDER)
        EndDeferWindowPos(hdwp)

    def OnNew(self, wParam, lParam, code):
        form = Form()
        form.ShowWindow()

    def OnExit(self, wParam, lParam, code):
        self.DestroyWindow()
        
    def OnInitMenuPopup(self, wParam, lParam):
        print "init pop"

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),                
                         CMD_HANDLER(ID_NEW, OnNew),
                         CMD_HANDLER(ID_EXIT, OnExit),
                         MSG_HANDLER(WM_INITMENUPOPUP, OnInitMenuPopup),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])


mainForm = Form()
mainForm.ShowWindow()
Run()

print "done"
