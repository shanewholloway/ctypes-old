from windows import *
from gdi import *
from ctypes import *

import weakref

#hndlMap = {} #maps windows handles to instances of disposable
hndlMap = weakref.WeakValueDictionary()

def globalWndProc(hWnd, nMsg, wParam, lParam):
    """The purpose of globalWndProc is to let each (python) window instance
    handle its own msgs, therefore is a mapping maintained from hWnd to window instance"""
    #if nMsg == WM_SIZE:
    #    print "WM_SIZE", hWnd, hndlMap.get(hWnd, None)
    #print "gwp: ", hWnd, nMsg, wParam, lParam, hndlMap.get(hWnd, None)
    

    handled = 0
    window = hndlMap.get(hWnd, None)
    if window:
         #let the window process its own msgs
        handled, result = window.WndProc(hWnd, nMsg, wParam, lParam)
        if not handled and window._class_: #its a subclassed window, try old window proc
            result = CallWindowProc(window._old_wnd_proc_, hWnd, nMsg, wParam, lParam)
            handled = 1
        
    if not handled:
        return DefWindowProc(hWnd, nMsg, wParam, lParam)
    else:
        return result

cGlobalWndProc = WndProc(globalWndProc)

def handle(obj):
    if not obj:
        return NULL
    elif hasattr(obj, 'handle'):
        return obj.handle
    else:
        return obj

def instanceFromHandle(handle):
    return hndlMap.get(handle, None)

def instanceOrHandle(handle):
    return hndlMap.get(handle, handle)

class MSG_MAP(object):
    def __init__(self, entries):
        self._msg_map_ = {}
        self._chained_ = []

        for entry in entries:
            entry.__install__(self)

    def Dispatch(self, receiver, hWnd, nMsg, wParam, lParam):
        handler = self._msg_map_.get(nMsg, None)
        if handler:
            res = handler(receiver, hWnd, nMsg, wParam, lParam)
            if res == None:
                return (1, 0) #assume handled and result = 0
            else:
                return res
        else:
            for msgMap in self._chained_:
                res = msgMap.Dispatch(receiver, hWnd, nMsg, wParam, lParam)
                if res:
                    handled, res = res
                    if handled:
                        return (handled, res)

        #nobody handled msg
        return (0, 0)

                 
class MSG_HANDLER(object):
    def __init__(self, msg, handler):
        self.msg, self.handler = msg, handler

    def __install__(self, msgMap):
        msgMap._msg_map_[self.msg] = self

    def __call__(self, receiver, hWnd, nMsg, wParam, lParam):
        return self.handler(receiver, wParam, lParam)

class CHAIN_MSG_MAP(object):
    def __init__(self, msgMap):
        self.msgMap = msgMap

    def __install__(self, msgMap):
        msgMap._chained_.append(self.msgMap)

class NTF_MAP(dict):
    def __call__(self, receiver, hWnd, nMsg, wParam, lParam):
        nmhdr = NMHDR.from_address(lParam)
        handler = self.get(str(nmhdr.code), None)
        if handler:
            return handler(receiver, hWnd, nMsg, wParam, lParam, nmhdr)
        else:
            return (0, 0)
        
class NTF_HANDLER(object):
    def __init__(self, code, handler):
        self.code, self.handler = code, handler

    def __install__(self, msgMap):
        notifMap = msgMap._msg_map_.setdefault(WM_NOTIFY, NTF_MAP())
        notifMap[str(self.code)] = self

    def __call__(self, receiver, hWnd, nMsg, wParam, lParam, nmhdr):
        return self.handler(receiver, wParam, lParam, nmhdr)

class CMD_MAP(dict):
    def __call__(self, receiver, hWnd, nMsg, wParam, lParam):
        code = LOWORD(wParam)
        handler = self.get(str(code), None)
        if handler:
            return handler(receiver, hWnd, nMsg, wParam, lParam, code)
        else:
            return (0, 0)

class CMD_HANDLER(object):
    def __init__(self, id, handler):
        self.id, self.handler = id, handler

    def __install__(self, msgMap):
        cmdMap = msgMap._msg_map_.setdefault(WM_COMMAND, CMD_MAP())
        cmdMap[str(self.id)] = self

    def __call__(self, receiver, hWnd, nMap, wParam, lParam, code):
        return self.handler(receiver, wParam, lParam, code)
    
class disposable(object):
    def __init__(self, handle):
        print '__init__', self, handle
        self.m_handle = handle
        hndlMap[handle] = self
        
    def getHandle(self):
        return self.m_handle

    handle = property(getHandle, None, None, "")

    def dispose(self):
        if self.m_handle:
            self.__dispose__()
            self.m_handle = None

    def __dispose__(self):
        raise "override this method"
        
    def __del__(self):
        print '__del__', self, self.m_handle
        self.dispose()

rcDefault = RECT(top = -2147483648, left = -2147483648,
                 bottom = 0, right = 0)    

hInstance = GetModuleHandle(NULL)

class Window(disposable):
    _class_ = ''    
    _class_ws_style_ = WS_OVERLAPPEDWINDOW
    _class_ws_ex_style_ = 0
    _class_icon_ = LoadIcon(NULL, IDI_APPLICATION)
    _class_icon_sm_ = LoadIcon(NULL, IDI_APPLICATION)
    _class_background_ = GetStockObject(WHITE_BRUSH)
    _class_style_ = 0
    _class_clip_children_and_siblings = 1
    
    _msg_map_ = MSG_MAP([])
    
    def __init__(self, title = "",
                 style = None,
                 exStyle = None,
                 parent = None,
                 menu = None,
                 rcPos = rcDefault,
                 orStyle = None,
                 orExStyle = None,
                 nandStyle = None,
                 nandExStyle = None):
        
        if not self._class_:
            wndClass = "python_wtl_%s" % str(self.__class__)
            #cls structure needs to stay on heap, therefore class attribute
            Window.cls = WNDCLASSEX()
            Window.cls.cbSize = sizeof(Window.cls)
            Window.cls.lpszClassName = wndClass
            Window.cls.hInstance = hInstance
            Window.cls.lpfnWndProc = cGlobalWndProc
            Window.cls.style = self._class_style_
            Window.cls.hbrBackground = self._class_background_
            Window.cls.hIcon = handle(self._class_icon_)
            Window.cls.hIconSm = handle(self._class_icon_sm_)
            Window.cls.hCursor = LoadCursor(NULL, IDC_ARROW)
            atom = RegisterClassEx(pointer(Window.cls))
        else:
            wndClass = self._class_

        if style is None:
            style = self._class_ws_style_

        if exStyle is None:
            exStyle = self._class_ws_ex_style_

        if orStyle:
            style |= orStyle

        if orExStyle:
            exStyle |= orExStyle

        if self._class_clip_children_and_siblings:
            style |= WS_CLIPCHILDREN
            style |= WS_CLIPSIBLINGS

        if nandStyle:
            style &= ~nandStyle
            
        if rcPos.left == -2147483648:
            nWidth = -2147483648
        else:
            nWidth = rcPos.right - rcPos.left
        if rcPos.top == -2147483648:
            nHeight = -2147483648
        else:
            nHeight = rcPos.bottom - rcPos.top

        hWnd = CreateWindowEx(exStyle,
                              wndClass,
                              title,
                              style,
                              rcPos.left,
                              rcPos.top,
                              nWidth,
                              nHeight,
                              handle(parent),
                              handle(menu),
                              hInstance,
                              0)
        
        disposable.__init__(self, hWnd)
        #print self, "created, hWnd: %d, style: %d, exstyle: %d" % (self.m_hWnd, style, exStyle)
        if self._class_:
            print "subclassing: ", self._class_
            self._old_wnd_proc_ = self.SubClass(cGlobalWndProc)

    def __dispose__(self):
        DestroyWindow(self.handle)

    def SubClass(self, newWndProc):
        return SetWindowLong(self.handle, GWL_WNDPROC, newWndProc)
    
    def ShowWindow(self, cmdShow = SW_SHOW):
        ShowWindow(self.handle, cmdShow)

    def GetClassLong(self, index):
        return GetClassLong(self.handle, index)

    def SetClassLong(self, index, dwNewLong):
        SetClassLong(self.handle, index, dwNewLong)
        
    def UpdateWindow(self):
        UpdateWindow(self.handle)

    def MoveWindow(self, x, y, nWidth, nHeight, bRepaint):
        MoveWindow(self.handle, x, y, nWidth, nHeight, bRepaint)

    def SetCapture(self):
        SetCapture(self.handle)
        
    def Invalidate(self, bErase = TRUE):
        InvalidateRect(self.handle, NULL, bErase)

    def InvalidateRect(self, rc, bErase = TRUE):
        InvalidateRect(self.handle, pointer(rc), bErase)

    def GetDCEx(self, hrgnClip, flags):
        return GetDCEx(self.handle, hrgnClip, flags)

    def ReleaseDC(self, hdc):
        ReleaseDC(self.handle, hdc)
        
    def BeginPaint(self, paintStruct):
        return BeginPaint(self.handle, pointer(paintStruct))

    def EndPaint(self, paintStruct):
        return EndPaint(self.handle, pointer(paintStruct))
        
    def DestroyWindow(self):
        DestroyWindow(self.handle)

    def GetClientRect(self):
        rc = RECT()
        GetClientRect(self.handle, pointer(rc))
        return rc

    clientRect = property(GetClientRect, None, None, "")

    def SetWindowPos(self, hWndInsertAfter, x, y, cx, cy, uFlags):
        SetWindowPos(self.handle, hWndInsertAfter, x, y, cx, cy, uFlags)
    
    def GetWindowRect(self):
        rc = RECT()
        GetWindowRect(self.handle, pointer(rc))
        return rc

    windowRect = property(GetWindowRect, None, None, "")

    def ScreenToClient(self, point):
        ScreenToClient(self.handle, pointer(point))
                       
    def SetRedraw(self, bRedraw):
        SendMessage(self.handle, WM_SETREDRAW, bRedraw, 0)

    class Interceptor(object):
        def __init__(self, receiver, window, msg_map):
            self.newProc = WndProc(self.WndProc)
            self.oldParentProc = window.SubClass(self.newProc)
            self._msg_map_ = msg_map
            self.receiver = receiver
            
        def WndProc(self, hWnd, nMsg, wParam, lParam):
            handled, res = self._msg_map_.Dispatch(self.receiver, hWnd, nMsg, wParam, lParam)
            if not handled:
                return CallWindowProc(self.oldParentProc, hWnd, nMsg, wParam, lParam)
            else:
                return res
            
            
    def Intercept(self, window, msgMap):
        return Window.Interceptor(self, window, msgMap)
    
    def WndProc(self, hWnd, nMsg, wParam, lParam):
        return self._msg_map_.Dispatch(self, hWnd, nMsg, wParam, lParam)
    
    def GetParent(self):
        return instanceOrHandle(GetParent(self.handle))
    
    def IsDialogMessage(self, lpmsg):
        return IsDialogMessage(self.handle, lpmsg)
    
    def PreTranslateMessage(self, msg):
        return 0

    def TranslateAccelerator(self, msg):
        return 0
        
class MenuBase(object):
    def AppendMenu(self, flags, idNewItem, lpNewItem):
        if flags == MF_STRING or flags == MF_SEPARATOR:
            AppendMenu(self.handle, flags, idNewItem, lpNewItem)
        elif flags & MF_POPUP:
            AppendMenu(self.handle, flags, handle(idNewItem), lpNewItem)
    
    def EnableMenuItem(self, uIDEnableItem, uEnable):
        EnableMenuItem(self.handle, uIDEnableItem, uEnable)
        
class Menu(MenuBase, disposable):
    def __init__(self):
        disposable.__init__(self, CreateMenu())
        
    def __dispose__(self):
       DestroyMenu(self.handle)
                   
class PopupMenu(MenuBase, disposable):
    def __init__(self):
        disposable.__init__(self, CreatePopupMenu())
        
    def __dispose__(self):
        DestroyMenu(self.handle)
    
class Bitmap(disposable):
    def __init__(self, path):
        disposable.__init__(self, LoadImage(NULL, path, IMAGE_BITMAP, 0, 0, LR_LOADFROMFILE))
        bm = BITMAP()
        GetObject(self.handle, sizeof(bm), pointer(bm))
        self.m_width, self.m_height = bm.bmWidth, bm.bmHeight

    def __dispose__(self):
        DeleteObject(self.handle)
        
    def getWidth(self):
        return self.m_width

    width = property(getWidth, None, None, "")
    
    def getHeight(self):
        return self.m_height

    height = property(getHeight, None, None, "")
        
class Icon(disposable):
    def __init__(self, path):
        disposable.__init__(self, LoadImage(NULL, path, IMAGE_ICON, 0, 0, LR_LOADFROMFILE))
        
    def __dispose__(self):
        DestroyIcon(self.handle)


#TODO allow the addition of more specific filters
class MessageLoop:
    def __init__(self):
        self.m_filters = {}

    def AddFilter(self, filter):
        self.m_filters[filter] = filter

    def RemoveFilter(self, filter):
        del self.m_filters[filter]
        
    def Run(self):
        msg = MSG()
        lpmsg = pointer(msg)
        while GetMessage(lpmsg, 0, 0, 0):
            if not self.PreTranslateMessage(msg):
                TranslateMessage(lpmsg)
                DispatchMessage(lpmsg)
                
                    
    def PreTranslateMessage(self, msg):
        for filter in self.m_filters:
            if filter.PreTranslateMessage(msg):
                return 1
        return 0
    
theMessageLoop = MessageLoop()

def GetMessageLoop():
    return theMessageLoop

def Run():
    theMessageLoop.Run()
    #hWndMap should be empty at this point, container widgets
    #should auto-dispose of their children! (somehow)
    ##print hndlMap

