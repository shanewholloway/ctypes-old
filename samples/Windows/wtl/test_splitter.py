from windows import *
from wtl import *
import splitter
import form
import list

def createTestChild(parent):

    lst = list.List(parent = parent, orExStyle = WS_EX_CLIENTEDGE)
    lst.InsertColumns([("blaat", 100), ("col2", 150)])
    for i in range(100):
        lst.InsertRow(i, ["blaat %d" % i, "blaat col2 %d" % i])

    return lst

class Form(form.Form):
    def __init__(self):
        self.menu = Menu()

        self.menuFile = PopupMenu()

        self.menuFile.AppendMenu(MF_SEPARATOR, 0, 0)
        self.menuFile.AppendMenu(MF_STRING, 1003, "&Exit")
        self.menu.AppendMenu(MF_POPUP, self.menuFile, "&File")


        form.Form.__init__(self, menu = self.menu, title = "Splitter Wnd test")      


        self.splitter = splitter.Splitter(parent = self,
                                          splitPos = self.clientRect.width / 2,
                                          splitWidth = 120)
        
        self.child1 = createTestChild(self)
        self.child2 = createTestChild(self)
        
        
        self.splitter.Add(0, self.child1)
        self.splitter.Add(1, self.child2)

    def OnSize(self, wParam, lParam):
        cx, cy = LOWORD(lParam), HIWORD(lParam)
        self.splitter.MoveWindow(0, 0, cx, cy, TRUE)

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_SIZE, OnSize),
                         CHAIN_MSG_MAP(form.Form._msg_map_)])

if __name__ == '__main__':
    app = Form()
    app.ShowWindow()
    Run()
