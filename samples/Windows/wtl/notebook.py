from windows import *
from wtl import *
import atl
import comctl
import gdi

class NoteBook(comctl.TabControl):
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN | WS_CLIPSIBLINGS
    _class_ws_ex_style_ = 0
    _class_background_ = 0
    
    def __init__(self, *args, **kwargs):
        apply(comctl.TabControl.__init__, (self,) + args, kwargs)
        hfnt = gdi.GetStockObject(gdi.DEFAULT_GUI_FONT)
        SendMessage(self.handle, WM_SETFONT, hfnt, 0)
        #intercept msgs tabctrl sends to parent in order to detect current
        #tab changes:
        self.interceptor = self.Intercept(self.GetParent(),
                                          self._msg_map2_)
                                          
        #remove the default CS_HREDRAW and CS_VREDRAW class styles from
        #tab ctrl, these produce much flicker!
        #may produce some artifacts, anybody got a solution?
        clsStyle = self.GetClassLong(GCL_STYLE)
        clsStyle &= ~CS_HREDRAW
        clsStyle &= ~CS_VREDRAW
        self.SetClassLong(GCL_STYLE, clsStyle)
        
    def _ResizeChild(self, child):
        if child:
            rc = self.GetClientRect()
            self.AdjustRect(0, rc)
            child.MoveWindow(rc.left, rc.top, rc.width, rc.height, TRUE)
            
    def GetChildAt(self, index):
        item = self.GetItem(index, TCIF_PARAM)
        return instanceFromHandle(item.lParam)
        
    def AddTab(self, index, title, child):
        item = TCITEM()
        item.mask = TCIF_TEXT | TCIF_PARAM
        item.pszText = title
        item.lParam = handle(child)
        self.InsertItem(index, item)
        self._ResizeChild(child)

    def OnSelChange(self, wParam, lParam, nmhdr):
        print "onselchange!"
        #new current tab
        child = self.GetChildAt(self.GetCurSel())
        if child:
            self._ResizeChild(child)
            child.ShowWindow(SW_SHOW)

    def OnSelChanging(self, wParam, lParam, nmhdr):
        print "onselchangng!"
        #current tab changing
        child = self.GetChildAt(self.GetCurSel())
        if child:
            child.ShowWindow(SW_HIDE)
        
    def OnSize(self, wParam, lParam):
        self.Invalidate() #slight flicker at tabs, but keeps artificats from showing up
        #maybe only invalidate areas not covert by child
        child = self.GetChildAt(self.GetCurSel())
        self._ResizeChild(child)
        return (0, 0)

    def OnEraseBackground(self, wParam, lParam):
        return (0, 0)

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         MSG_HANDLER(WM_ERASEBKGND, OnEraseBackground)])

    _msg_map2_ = MSG_MAP([NTF_HANDLER(comctl.TCN_SELCHANGE, OnSelChange),
                          NTF_HANDLER(comctl.TCN_SELCHANGING, OnSelChanging)])
                       
    
