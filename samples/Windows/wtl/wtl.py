from windows import *
from ctypes import sizeof

hInstance = GetModuleHandle(NULL)

hWndMap = {} #maps platform window handles to instances of Window

def globalWndProc(hWnd, nMsg, wParam, lParam):
    """The purpose of globalWndProc is to let each (python) window instance
    handle its own msgs, therefore a mapping maintained from hWnd to window instance"""
    #print "gwndP", hWnd, nMsg
    if nMsg == WM_NCCREATE:
        #window handle has become valid for newly created window
        #the window passed its id in createstruct
        #we can now complete the mapping from hWnd->windowInstance
        createStruct = CREATESTRUCT.from_address(lParam)
        windowId = createStruct.lpCreateParams
        window = hWndMap[windowId] #find back windowInstance
        del hWndMap[windowId]
        hWndMap[hWnd] = window #now map instance by hWnd instead of by id
    elif nMsg == WM_NCDESTROY:
        window = None
        del hWndMap[hWnd]
    else: 
        window = hWndMap.get(hWnd, None)

    if window: #let the window process its own msgs
        return window.WndProc(hWnd, nMsg, wParam, lParam)
    else: #do default msg processing
        return DefWindowProc(hWnd, nMsg, wParam, lParam)

def handle(obj):
    if not obj:
        return NULL
    elif hasattr(obj, 'handle'):
        return obj.handle
    else:
        return NULL
    
class Window(object):
    _msg_map_ = {}
    _wnd_class_ = ''
    _def_style_ = WS_OVERLAPPEDWINDOW
    _def_ex_style_ = 0
    
    def __init__(self, title = "",
                 style = None,
                 exStyle = None,
                 parent = None,
                 menu = None):
        if not self._wnd_class_:
            wndClass = str(self.__class__)
            #cls structure needs to stay on heap, therefore class attribute
            Window.cls = WNDCLASSEX()
            Window.cls.cbSize = sizeof(Window.cls)
            Window.cls.lpszClassName = wndClass
            Window.cls.hInstance = hInstance
            Window.cls.lpfnWndProc = WndProc(globalWndProc)
            Window.cls.style = CS_HREDRAW | CS_VREDRAW
            Window.cls.hbrBackground = GetStockObject(WHITE_BRUSH)
            Window.cls.hIcon = LoadIcon(NULL, IDI_APPLICATION)
            Window.cls.hIconSm = LoadIcon(NULL, IDI_APPLICATION)
            Window.cls.hCursor = LoadCursor(NULL, IDC_ARROW)
            atom = RegisterClassEx(pointer(Window.cls))
        else:
            wndClass = self._wnd_class_

        if style is None:
            style = self._def_style_

        if exStyle is None:
            exStyle = self._def_ex_style_
            
        style |= WS_CLIPCHILDREN #to prevent flicker
        style |= WS_CLIPSIBLINGS

        #store self in hWnd map, so that we can map this window instance
        #and the corresponding window handle when it becomes available
        #(in WM_NCCREATE)
        hWndMap[id(self)] = self
        self.m_hWnd = CreateWindowEx(exStyle,
                                     wndClass,
                                     title,
                                     style,
                                     CW_USEDEFAULT,
                                     CW_USEDEFAULT,
                                     CW_USEDEFAULT,
                                     CW_USEDEFAULT,
                                     handle(parent),
                                     handle(menu),
                                     hInstance,
                                     id(self)) #pass my id as create param

    def ShowWindow(self, cmdShow = SW_SHOW):
        ShowWindow(self.handle, cmdShow)
        
    def UpdateWindow(self):
        UpdateWindow(self.handle)

    def MoveWindow(self, x, y, nWidth, nHeight, bRepaint):
        MoveWindow(self.handle, x, y, nWidth, nHeight, bRepaint)

    def DestroyWindow(self):
        DestroyWindow(self.handle)
        
    def getHandle(self):
        return self.m_hWnd

    handle = property(getHandle, None, None, "")
    
    def WndProc(self, hWnd, nMsg, wParam, lParam):
        handler = self._msg_map_.get(nMsg, None)
        if handler:
            handler(self, wParam, lParam)
        else:
            return DefWindowProc(hWnd, nMsg, wParam, lParam)

class Frame(Window):
    _def_style = WS_OVERLAPPEDWINDOW | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN |\
                 WS_OVERLAPPED
    _def_ex_style_ = WS_EX_LEFT | WS_EX_LTRREADING | WS_EX_RIGHTSCROLLBAR | WS_EX_WINDOWEDGE
    
class StatusBar(Window):
    _wnd_class_ = STATUSCLASSNAME
    _def_style_ = WS_CHILD | WS_BORDER | WS_VISIBLE | SBS_SIZEGRIP
    
class ComboBox(Window):
    _wnd_class_ = WC_COMBOBOXEX
    _def_style_ = WS_BORDER | WS_VISIBLE | WS_CHILD | CBS_DROPDOWN
        
class Toolbar(Window):
    _wnd_class_ = TOOLBARCLASSNAME
    _def_style_ = WS_CHILDWINDOW | WS_VISIBLE | WS_CLIPSIBLINGS | WS_CLIPCHILDREN|\
                  TBSTYLE_TRANSPARENT | TBSTYLE_REGISTERDROP | TBSTYLE_FLAT | TBSTYLE_LIST |\
                  CCS_NODIVIDER | CCS_NOPARENTALIGN | CCS_NORESIZE | CCS_TOP
    _def_ex_style_ = WS_EX_LEFT | WS_EX_LTRREADING | WS_EX_RIGHTSCROLLBAR | WS_EX_TOOLWINDOW

    def __init__(self, *args, **kwargs):
        apply(Window.__init__, (self,) + args, kwargs)
        SendMessage(self.handle, TB_BUTTONSTRUCTSIZE, sizeof(TBBUTTON), 0)

        tbButt = TBBUTTON()
        tbButt.iBitmap = I_IMAGENONE
        tbButt.idCommand = 1001
        tbButt.fsState = TBSTATE_ENABLED
        tbButt.fsStyle = BTNS_SHOWTEXT|TBSTYLE_DROPDOWN
        tbButt.iString = "&File"

        SendMessage(self.handle, TB_ADDBUTTONS, 1, pointer(tbButt))


        tbButt = TBBUTTON()
        tbButt.iBitmap = I_IMAGENONE
        tbButt.idCommand = 1002
        tbButt.fsState = TBSTATE_ENABLED
        tbButt.fsStyle = BTNS_SHOWTEXT|TBSTYLE_DROPDOWN
        tbButt.iString = "&Edit"

        SendMessage(self.handle, TB_ADDBUTTONS, 1, pointer(tbButt))

class Rebar(Window):
    _wnd_class_ = REBARCLASSNAME

    def __init__(self,
                 style = WS_CHILDWINDOW|WS_VISIBLE|WS_CLIPSIBLINGS|WS_CLIPCHILDREN|WS_BORDER|\
                 RBS_VARHEIGHT|RBS_BANDBORDERS|RBS_AUTOSIZE|RBS_DBLCLKTOGGLE|RBS_REGISTERDROP|\
                 CCS_NODIVIDER|CCS_NOPARENTALIGN|CCS_TOP,
                 exStyle = WS_EX_LEFT|WS_EX_LTRREADING|WS_EX_RIGHTSCROLLBAR|WS_EX_TOOLWINDOW,
                 parent = NULL):
        Window.__init__(self, style = style, exStyle = exStyle,
                        parent = parent)
        rebarInfo = REBARINFO()
        rebarInfo.cbSize = sizeof(REBARINFO)
        rebarInfo.fMask = 0
        rebarInfo.himl = NULL
        SendMessage(self.handle, RB_SETBARINFO, 0, pointer(rebarInfo))
        
        rbBand = REBARBANDINFO()
        rbBand.cbSize = sizeof(REBARBANDINFO)
        rbBand.fMask = RBBIM_CHILD | RBBIM_CHILDSIZE | RBBIM_SIZE | RBBIM_STYLE
        rbBand.fStyle = RBBS_CHILDEDGE# | RBBS_GRIPPERALWAYS# | RBBS_USECHEVRON

        self.menuBar = Toolbar(parent = self)
        #rbBand.lpText     = "Combo Box"
        rbBand.hwndChild  = self.menuBar.handle
        rbBand.cxMinChild = 0
        rbBand.cyMinChild = 25#rc.bottom - rc.top
        rbBand.cx         = 200

        #// Add the band that has the combo box.
        SendMessage(self.handle, RB_INSERTBAND, -1, pointer(rbBand))

        rbBand = REBARBANDINFO()
        rbBand.cbSize = sizeof(REBARBANDINFO)
        rbBand.fMask = RBBIM_TEXT | RBBIM_CHILD | RBBIM_CHILDSIZE | RBBIM_SIZE | RBBIM_STYLE
        rbBand.fStyle = RBBS_CHILDEDGE | RBBS_GRIPPERALWAYS | RBBS_BREAK

        hwndCB = ComboBox(parent = self).handle        
        #rc = RECT()
        #GetWindowRect(hwndCB, pointer(rc))
        rbBand.lpText     = "Address"
        rbBand.hwndChild  = hwndCB
        rbBand.cxMinChild = 0
        rbBand.cyMinChild = 25#rc.bottom - rc.top
        rbBand.cx         = 200

        #// Add the band that has the combo box.
        SendMessage(self.handle, RB_INSERTBAND, -1, pointer(rbBand))



        
class Menu(object):
    def __init__(self):
        self.m_hMenu = CreateMenu()

    def getHandle(self):
        return self.m_hMenu

    handle = property(getHandle, None, None, "")
    
    def AppendMenu(self, flags, idNewItem, lpNewItem):
        AppendMenu(self.handle, flags, idNewItem, lpNewItem)
                   
    def __del__(self):
        if self.m_hMenu:
            DestroyMenu(self.m_hMenu)
            self.m_hMenu = None
            
        
def Run():
    lpmsg = pointer(MSG())

    while GetMessage(lpmsg, 0, 0, 0):
        TranslateMessage(lpmsg)
        DispatchMessage(lpmsg)

    #hWndMap should be empty at this point, container widgets
    #should auto-dispose of their children! (somehow)
    print hWndMap
