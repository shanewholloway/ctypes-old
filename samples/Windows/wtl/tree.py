from windows import *
from wtl import *
import comctl

class Tree(comctl.TreeView):
    def __init__(self, *args, **kwargs):
        apply(comctl.TreeView.__init__, (self,) + args, kwargs)        
        self.interceptor = self.Intercept(self.GetParent(), self._msg_map2_)

    def OnItemExpanding(self, wParam, lParam, nmhdr):
        print "item expanding"
        
    _msg_map2_ = MSG_MAP([NTF_HANDLER(comctl.TVN_ITEMEXPANDING, OnItemExpanding)])
                         
