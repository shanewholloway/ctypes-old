from windows import *
import wtl

class MyWindow(wtl.Frame):
    def __init__(self):
        self.menu = wtl.Menu()
        #self.menu.AppendMenu(MF_STRING, 101, "Blaat")
        wtl.Window.__init__(self, "Real Slick Looking Windows Application in 100% Python")        
        self.statusBar = wtl.StatusBar(parent = self)
        self.rebar = wtl.Rebar(parent = self)
        #print self.rebar.handle
        #self.comboBox = wtl.ComboBox(parent = self)
        #print self.comboBox.handle
        
    def OnDestroy(self, wParam, lParam):
        self.statusBar.DestroyWindow()
        PostQuitMessage(0)
        return 0

    def OnSize(self, wParam, lParam):
        self.statusBar.MoveWindow(0, HIWORD(lParam) - 10, LOWORD(lParam),
                                  HIWORD(lParam), FALSE)
        #print LOWORD(lParam), HIWORD(lParam)
        self.rebar.MoveWindow(0, 0, LOWORD(lParam), 20, FALSE) 

    _msg_map_ = {WM_DESTROY: OnDestroy,
                 WM_SIZE: OnSize}
    

iccex = INITCOMMONCONTROLSEX()
iccex.dwSize = sizeof(INITCOMMONCONTROLSEX)
iccex.dwICC = ICC_COOL_CLASSES | ICC_USEREX_CLASSES
InitCommonControlsEx(pointer(iccex))

w = MyWindow()        
w.ShowWindow()
w.UpdateWindow()

wtl.Run()
