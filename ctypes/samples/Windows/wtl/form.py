from windows import *
from wtl import *

EXIT_NONE = 0
EXIT_ONDESTROY = 1
EXIT_ONLASTDESTROY = 2

class Form(Window):
    _class_ws_style = WS_OVERLAPPEDWINDOW | WS_VISIBLE | WS_OVERLAPPED
    _class_ws_ex_style_ = WS_EX_LEFT | WS_EX_LTRREADING | WS_EX_RIGHTSCROLLBAR | \
                          WS_EX_WINDOWEDGE | WS_EX_APPWINDOW

    _class_accels_ = []
    _haccel_ = 0

    _class_form_exit_ = EXIT_ONDESTROY
    _class_form_count_ = 0
    
    def __init__(self, *args, **kwargs):
        apply(Window.__init__, (self,) + args, kwargs)        
        self.CreateAccels()
        GetMessageLoop().AddFilter(self) #TODO remove on destroy
        Form._class_form_count_ += 1
        
    def CreateAccels(self):
        if self._class_accels_ and not Form._haccel_:
            accels = (ACCEL * len(self._class_accels_))()
            for i in range(len(self._class_accels_)):
                accels[i].fVirt = self._class_accels_[i][0]
                accels[i].key   = self._class_accels_[i][1]
                accels[i].cmd   = self._class_accels_[i][2]
            Form._haccel_ = CreateAcceleratorTable(pointer(accels), len(self._class_accels_))
        
    def PreTranslateMessage(self, msg):
        if Form._haccel_:            
            return TranslateAccelerator(self.handle, Form._haccel_, pointer(msg))
        else:
            return 0
    
    def OnDestroy(self, wParam, lParam):
        Form._class_form_count_ -= 1
        if self._class_form_exit_ == EXIT_ONDESTROY:
            PostQuitMessage(0)
        elif self._class_form_exit_ == EXIT_ONLASTDESTROY and \
             self._class_form_count_ == 0:
            PostQuitMessage(0)

        GetMessageLoop().RemoveFilter(self)
        #TODO dispose Accel Table

    _msg_map_ = MSG_MAP([MSG_HANDLER(WM_DESTROY, OnDestroy)])
        


    
    

