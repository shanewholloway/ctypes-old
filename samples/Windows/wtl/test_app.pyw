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
import comdlg

comctl.InitCommonControls(comctl.ICC_LISTVIEW_CLASSES | comctl.ICC_COOL_CLASSES |\
                          comctl.ICC_USEREX_CLASSES)

ID_NEW = 1001
ID_EXIT = 1002
ID_OPEN = 1008

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
        print nmtv.ptDrag
        print self.GetParent()
        
    _msg_map_ = MSG_MAP([NTF_HANDLER(comctl.TVN_ITEMEXPANDING, OnItemExpanding),
                         NTF_HANDLER(comctl.TVN_SELCHANGED, OnSelectionChanged)])

class Form(form.Form):
    _class_icon_ = Icon("COW.ICO")
    _class_icon_sm_ = _class_icon_
    _class_background_ = 0
    _class_accels_ = [(FCONTROL|FVIRTKEY, ord("O"), ID_OPEN),
                      (FCONTROL|FVIRTKEY, ord("N"), ID_NEW)]
    _class_form_exit_ = form.EXIT_ONLASTDESTROY

    _class_form_status_msgs_ = {ID_NEW: "Creates a new window."}
    
    def __init__(self):
        self.CreateMenu()
        
        form.Form.__init__(self,
                           menu = self.menu,
                           title = "Supervaca al Rescate!")      

        self.noteBook = notebook.NoteBook(parent = self,
                                      orExStyle = WS_EX_CLIENTEDGE)
        
        self.ie = atl.AxWebControl("http://www.python.org",
                                   parent = self.noteBook,
                                   orExStyle = WS_EX_CLIENTEDGE)
        
        self.list = list.List(parent = self.noteBook,
                              orExStyle = WS_EX_CLIENTEDGE)
        
        self.list.InsertColumns([("blaat", 100), ("col2", 150)])
        self.list.SetRedraw(0)
        for i in range(100):
            self.list.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])
        self.list.SetRedraw(1)
    
        
        self.noteBook.AddTab(0, "blaat1", self.ie)
        self.noteBook.AddTab(1, "blaat2", self.list)

        

        self.statusBar = comctl.StatusBar(parent = self)

                
        self.tree = Tree(parent = self,
                         orExStyle = WS_EX_CLIENTEDGE)
        

        self.splitter = splitter.Splitter(parent = self, splitPos = 150)
        self.splitter.Add(0, self.tree)
        self.splitter.Add(1, self.noteBook)

    def CreateMenu(self):
        self.menu = Menu()
    
        self.menuFile = PopupMenu()
        self.menuFile.AppendMenu(MF_STRING, ID_NEW, "&New\tCtrl+N")
        self.menuFile.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuFile.AppendMenu(MF_STRING, ID_OPEN, "&Open...\tCtrl+O")
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

    def OnSize(self, event):
        cx, cy = event.size

        statusBarHeight = self.statusBar.windowRect.height
        
        hdwp = BeginDeferWindowPos(2)
        DeferWindowPos(hdwp, self.statusBar.handle, NULL, 0, cy - statusBarHeight,
                       cx, statusBarHeight, SWP_NOACTIVATE | SWP_NOZORDER)
        DeferWindowPos(hdwp, self.splitter.handle, NULL, 0, 0,
                       cx, cy - statusBarHeight, SWP_NOACTIVATE | SWP_NOZORDER)
        EndDeferWindowPos(hdwp)

    def OnNew(self, event):
        form = Form()
        form.ShowWindow()

    def OnExit(self, event):
        self.DestroyWindow()
        
    def OnInitMenuPopup(self, event):
        print "init pop"

    def OnOpen(self, event):
        ofd = comdlg.OpenFileDialog(parent = self)
        ofd.DoModal()
        print "path: '%s'" % ofd.path.strip()
        
    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),                
                         CMD_HANDLER(ID_NEW, OnNew),
                         CMD_HANDLER(ID_EXIT, OnExit),
                         CMD_HANDLER(ID_OPEN, OnOpen),
                         MSG_HANDLER(WM_INITMENUPOPUP, OnInitMenuPopup),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])


mainForm = Form()
mainForm.ShowWindow()
Run()

print "done"
