from ctypes import windll, cdll, Structure, pointer, WinError, CFunction, sizeof

WIN32_IE = 0x0550

#TODO: auto unicode selection,
#if unicode:
#  CreateWindowEx = windll.user32.CreateWindowExW
#else:
#  CreateWindowEx = windll.user32.CreateWindowExA
#etc, etc

#TODO split common ctrl stuff into commctrl.py

def ValidHandle(value):
    if value == 0:
        raise WinError()
    else:
        return value

class WndProc(CFunction):
    _types_ = 'iiii'
    _stdcall_ = 1
    
class WNDCLASSEX(Structure):
    _fields_ = [("cbSize", "I"),
                ("style",  "I"),
                ("lpfnWndProc", WndProc),
                ("cbClsExtra", "i"),
                ("cbWndExtra", "i"),
                ("hInstance", "I"),
                ("hIcon", "I"),
                ("hCursor", "I"),
                ("hbrBackground", "I"),
                ("lpszMenuName", "z"),
                ("lpszClassName", "z"),
                ("hIconSm", "I")]

class POINT(Structure):
    _fields_ = [("x", "I"),
                ("y", "I")]

    def __str__(self):
        return "POINT {x: %d, y: %d}" % (self.x, self.y)

class RECT(Structure):
    _fields_ = [("left", "i"),
                ("top", "i"),
                ("right", "i"),
                ("bottom", "i")]

    def __str__(self):
        return "RECT {left: %d, top: %d, right: %d, bottom: %d}" % (self.left, self.top,
                                                                    self.right, self.bottom)

    def getHeight(self):
        return self.bottom - self.top

    height = property(getHeight, None, None, "")

    def getWidth(self):
        return self.right - self.left

    width = property(getWidth, None, None, "")
    
class MSG(Structure):
    _fields_ = [("hWnd", "I"),
                ("message", "I"),
                ("wParam", "I"),
                ("lParam", "I"),
                ("time", "I"),
                ("pt", POINT)]

class ACCEL(Structure):
    _fields_ = [("fVirt", "b"),
                ("key", "h"),
                ("cmd", "h")]
    
class CREATESTRUCT(Structure):
    _fields_ = [("lpCreateParams", "I"),
                ("hInstance", "I"),
                ("hMenu", "I"),
                ("hwndParent", "I"),
                ("cx", "i"),
                ("cy", "i"),
                ("x", "i"),
                ("y", "i"),
                ("style", "I"),
                ("lpszName", "z"),
                ("lpszClass", "z"),
                ("dwExStyle", "I")]

class INITCOMMONCONTROLSEX(Structure):
    _fields_ = [("dwSize", "I"),
                ("dwICC", "I")]

class REBARINFO(Structure):
    _fields_ = [("cbSize", "I"),
                ("fMask", "I"),
                ("himl", "I")]

class REBARBANDINFO(Structure):
    _fields_ = [("cbSize", "I"),
                ("fMask", "i"),
                ("fStyle", "i"),
                ("clrFore", "I"),
                ("clrBack", "I"),
                ("lpText", "z"),
                ("cch", "I"),
                ("iImage", "i"),
                ("hwndChild", "I"),
                ("cxMinChild", "i"),
                ("cyMinChild", "i"),
                ("cx", "i"),
                ("hbmBack", "I"),
                ("wID", "I"),
                ("cyChild", "I"),
                ("cyMaxChild", "I"),
                ("cyIntegral", "I"),
                ("cxIdeal", "I"),
                ("lParam", "I"),
                ("cxHeader", "I")]


class TBBUTTON(Structure):
    _fields_ = [("iBitmap", "i"),
                ("idCommand", "i"),
                ("fsState", "B"),
                ("fsStyle", "B"),
                ("bReserved", "2s"),
                ("dwData", "I"),
                ("iString", "I")]

class TBBUTTONINFO(Structure):
    _fields_ = [("cbSize", "I"),
                ("dwMask", "I"),
                ("idCommand", "i"),
                ("iImage", "i"),
                ("fsState", "B"),
                ("fsStyle", "B"),
                ("cx", "H"),
                ("lParam", "I"),
                ("pszText", "z"),
                ("cchText", "i")]

class NMHDR(Structure):
    _fields_ = [("hwndFrom", "I"),
                ("idFrom", "I"),
                ("code", "I")]

class PAINTSTRUCT(Structure):
    _fields_ = [("hdc", "I"),
                ("fErase", "i"),
                ("rcPaint", RECT),
                ("fRestore", "i"),
                ("fIncUpdate", "i"),
                ("rgbReserved", "32s")]

class TVITEMEX(Structure):
    _fields_ = [("mask", "I"),
                ("hItem", "I"),
                ("state", "I"),
                ("stateMask", "I"),
                ("pszText", "z"),
                ("cchTextMax", "i"),
                ("iImage", "i"),
                ("iSelectedImage", "i"),
                ("cChildren", "i"),
                ("lParam", "I"),
                ("iIntegral", "i")]

class TVINSERTSTRUCT(Structure):
    _fields_ = [("hParent", "i"),
                ("hInsertAfter", "i"),
                ("itemex", TVITEMEX)]

class TCITEM(Structure):
    _fields_ = [("mask", "I"),
                ("dwState", "I"),
                ("dwStateMask", "I"),
                ("pszText", "z"),
                ("cchTextMax", "i"),
                ("iImage", "i"),
                ("lParam", "I")]
    
TVIF_TEXT    = 1

TVI_ROOT     = 0xFFFF0000
TVI_FIRST    = 0xFFFF0001
TVI_LAST     = 0xFFFF0002
TVI_SORT     = 0xFFFF0003

TV_FIRST = 0x1100
TVM_INSERTITEMA =     TV_FIRST
TVM_INSERTITEMW =    (TV_FIRST+50)
TVM_INSERTITEM = TVM_INSERTITEMA
TVM_SETIMAGELIST =    (TV_FIRST+9)


TVS_HASBUTTONS =       1
TVS_HASLINES = 2
TVS_LINESATROOT =      4
TVS_EDITLABELS  =      8
TVS_DISABLEDRAGDROP =  16
TVS_SHOWSELALWAYS =   32
TVS_CHECKBOXES =  256
TVS_TOOLTIPS = 128
TVS_RTLREADING = 64
TVS_TRACKSELECT = 512
TVS_FULLROWSELECT = 4096
TVS_INFOTIP = 2048
TVS_NONEVENHEIGHT = 16384
TVS_NOSCROLL  = 8192
TVS_SINGLEEXPAND  =1024
TVS_NOHSCROLL   =     0x8000

def LOWORD(dword):
    return dword & 0x0000ffff

def HIWORD(dword):
    return dword >> 16

TRUE = 1
FALSE = 0
NULL = 0

IDI_APPLICATION = 32512
IDC_ARROW = 32512
SW_SHOW = 5
SW_HIDE = 0

WM_DESTROY = 2
WM_SETREDRAW = 11
WM_PAINT = 15
WM_MOUSEMOVE = 512
WM_MOUSEHOVER = 0x2A1
WM_MOUSELEAVE = 0x2A3
WM_LBUTTONDOWN = 513
WM_LBUTTONUP = 514
WM_LBUTTONDBLCLK = 515
WM_KEYDOWN = 256
WM_KEYUP = 257
WM_KEYFIRST = 256
WM_KEYLAST = 264
WM_COMMAND = 273
WM_INITMENUPOPUP = 279
WM_SETFONT =48
WM_GETFONT =49
WM_SETCURSOR = 32
WM_CAPTURECHANGED = 533
WM_ERASEBKGND = 20

CS_HREDRAW = 2
CS_VREDRAW = 1
WHITE_BRUSH = 0


WS_BORDER	= 0x800000
WS_CAPTION	= 0xc00000
WS_CHILD	= 0x40000000
WS_CHILDWINDOW	= 0x40000000
WS_CLIPCHILDREN = 0x2000000
WS_CLIPSIBLINGS = 0x4000000
WS_DISABLED	= 0x8000000
WS_DLGFRAME	= 0x400000
WS_GROUP	= 0x20000
WS_HSCROLL	= 0x100000
WS_ICONIC	= 0x20000000
WS_MAXIMIZE	= 0x1000000
WS_MAXIMIZEBOX	= 0x10000
WS_MINIMIZE	= 0x20000000
WS_MINIMIZEBOX	= 0x20000
WS_OVERLAPPED	= 0
WS_OVERLAPPEDWINDOW = 0xcf0000
WS_POPUP	= 0x80000000
WS_POPUPWINDOW	= 0x80880000
WS_SIZEBOX	= 0x40000
WS_SYSMENU	= 0x80000
WS_TABSTOP	= 0x10000
WS_THICKFRAME	= 0x40000
WS_TILED	= 0
WS_TILEDWINDOW	= 0xcf0000
WS_VISIBLE	= 0x10000000
WS_VSCROLL	= 0x200000

WS_EX_TOOLWINDOW = 128
WS_EX_LEFT = 0
WS_EX_LTRREADING = 0
WS_EX_RIGHTSCROLLBAR = 0
WS_EX_WINDOWEDGE = 256
WS_EX_STATICEDGE = 0x20000
WS_EX_CLIENTEDGE = 512
WS_EX_OVERLAPPEDWINDOW   =     0x300
WS_EX_APPWINDOW    =   0x40000
WM_NCCREATE = 129
WM_NCDESTROY = 130
WM_SIZE = 5
WM_NOTIFY = 78
WM_MOVE = 3

SBS_BOTTOMALIGN = 4
SBS_HORZ = 0
SBS_LEFTALIGN = 2
SBS_RIGHTALIGN = 4
SBS_SIZEBOX = 8
SBS_SIZEBOXBOTTOMRIGHTALIGN = 4
SBS_SIZEBOXTOPLEFTALIGN = 2
SBS_SIZEGRIP = 16
SBS_TOPALIGN = 2
SBS_VERT = 1

RBS_VARHEIGHT = 512

CCS_NODIVIDER =	64
CCS_NOPARENTALIGN = 8
CCS_NORESIZE = 4
CCS_TOP = 1


CBS_DROPDOWN = 2

MF_ENABLED    =0
MF_GRAYED     =1
MF_DISABLED   =2
MF_BITMAP     =4
MF_CHECKED    =8
MF_MENUBARBREAK= 32
MF_MENUBREAK  =64
MF_OWNERDRAW  =256
MF_POPUP      =16
MF_SEPARATOR  =0x800
MF_STRING     =0
MF_UNCHECKED  =0
MF_DEFAULT    =4096
MF_SYSMENU    =0x2000
MF_HELP       =0x4000
MF_END        =128
MF_RIGHTJUSTIFY=       0x4000
MF_MOUSESELECT =       0x8000
MF_INSERT= 0
MF_CHANGE= 128
MF_APPEND= 256
MF_DELETE= 512
MF_REMOVE= 4096
MF_USECHECKBITMAPS= 512
MF_UNHILITE= 0
MF_HILITE= 128
MF_BYCOMMAND=  0
MF_BYPOSITION= 1024
MF_UNCHECKED=  0
MF_HILITE =    128
MF_UNHILITE =  0
 

WM_USER = 1024
RB_SETBARINFO = WM_USER + 4
RB_GETBANDCOUNT = WM_USER +  12
RB_INSERTBANDA = WM_USER + 1
RB_INSERTBANDW = WM_USER + 10

RB_INSERTBAND = RB_INSERTBANDA

RBBIM_STYLE = 1
RBBIM_COLORS = 2
RBBIM_TEXT = 4
RBBIM_IMAGE = 8
RBBIM_CHILD = 16
RBBIM_CHILDSIZE = 32
RBBIM_SIZE = 64
RBBIM_BACKGROUND = 128
RBBIM_ID = 256
RBBIM_IDEALSIZE = 0x00000200


RBBS_BREAK = 1
RBBS_FIXEDSIZE = 2
RBBS_CHILDEDGE = 4
RBBS_HIDDEN = 8
RBBS_NOVERT = 16
RBBS_FIXEDBMP = 32
RBBS_VARIABLEHEIGHT = 64
RBBS_GRIPPERALWAYS = 128
RBBS_NOGRIPPER = 256

RBS_TOOLTIPS = 256
RBS_VARHEIGHT = 512
RBS_BANDBORDERS = 1024
RBS_FIXEDORDER = 2048

RBS_REGISTERDROP = 4096
RBS_AUTOSIZE = 8192
RBS_VERTICALGRIPPER = 16384
RBS_DBLCLKTOGGLE = 32768

TBSTYLE_FLAT = 2048
TBSTYLE_LIST = 4096
TBSTYLE_DROPDOWN = 8
TBSTYLE_TRANSPARENT = 0x8000
TBSTYLE_REGISTERDROP = 0x4000
TBSTYLE_BUTTON = 0x0000
TBSTYLE_AUTOSIZE = 0x0010
    
TB_BUTTONSTRUCTSIZE = WM_USER+30
TB_ADDBUTTONS       = WM_USER+20
TB_INSERTBUTTONA    = WM_USER + 21
TB_INSERTBUTTON     = WM_USER + 21
TB_BUTTONCOUNT      = WM_USER + 24
TB_GETITEMRECT      = WM_USER + 29
TB_SETBUTTONINFOW  =  WM_USER + 64
TB_SETBUTTONINFOA  =  WM_USER + 66
TB_SETBUTTONINFO   =  TB_SETBUTTONINFOA
TB_SETIMAGELIST    =  WM_USER + 48
TB_SETDRAWTEXTFLAGS =  WM_USER + 70

TBIF_TEXT = 0x00000002

DT_NOPREFIX   =      0x00000800
DT_HIDEPREFIX =      1048576

I_IMAGENONE = -2
TBSTATE_ENABLED = 4

BTNS_SHOWTEXT = 0x00000040
CW_USEDEFAULT = 0x80000000

COLOR_3DFACE = 15

BF_LEFT      = 1
BF_TOP       = 2
BF_RIGHT     = 4
BF_BOTTOM    = 8

BDR_RAISEDOUTER =      1
BDR_SUNKENOUTER =      2
BDR_RAISEDINNER =      4
BDR_SUNKENINNER =      8
BDR_OUTER    = 3
BDR_INNER    = 0xc
BDR_RAISED   = 5
BDR_SUNKEN   = 10

EDGE_RAISED  = (BDR_RAISEDOUTER|BDR_RAISEDINNER)
EDGE_SUNKEN  = (BDR_SUNKENOUTER|BDR_SUNKENINNER)
EDGE_ETCHED  = (BDR_SUNKENOUTER|BDR_RAISEDINNER)
EDGE_BUMP    = (BDR_RAISEDOUTER|BDR_SUNKENINNER)

IDC_SIZEWE = 32644

TCIF_TEXT    =1
TCIF_IMAGE   =2
TCIF_RTLREADING=      4
TCIF_PARAM  = 8


TCS_MULTILINE = 512

MK_LBUTTON    = 1
MK_RBUTTON    = 2
MK_SHIFT      = 4
MK_CONTROL    = 8
MK_MBUTTON    = 16

#commctl:
ILC_COLOR = 0
ILC_COLOR4 = 4
ILC_COLOR8 = 8
ILC_COLOR16 = 16
ILC_COLOR24 = 24
ILC_COLOR32 = 32
ILC_COLORDDB = 254
ILC_MASK = 1
ILC_PALETTE = 2048

IMAGE_BITMAP = 0
IMAGE_ICON = 1

LR_LOADFROMFILE = 16

LVSIL_NORMAL = 0
LVSIL_SMALL  = 1
LVSIL_STATE  = 2

TVSIL_NORMAL = 0
TVSIL_STATE  = 2

SRCCOPY = 0xCC0020

GWL_WNDPROC = -4

HWND_BOTTOM = 1

SWP_DRAWFRAME= 32
SWP_FRAMECHANGED= 32
SWP_HIDEWINDOW= 128
SWP_NOACTIVATE= 16
SWP_NOCOPYBITS= 256
SWP_NOMOVE= 2
SWP_NOSIZE= 1
SWP_NOREDRAW= 8
SWP_NOZORDER= 4
SWP_SHOWWINDOW= 64
SWP_NOOWNERZORDER =512
SWP_NOREPOSITION= 512
SWP_NOSENDCHANGING= 1024
SWP_DEFERERASE= 8192
SWP_ASYNCWINDOWPOS=  16384

DCX_WINDOW = 1
DCX_CACHE = 2
DCX_PARENTCLIP = 32
DCX_CLIPSIBLINGS= 16
DCX_CLIPCHILDREN= 8
DCX_NORESETATTRS= 4
DCX_LOCKWINDOWUPDATE= 0x400
DCX_EXCLUDERGN= 64
DCX_INTERSECTRGN =128
DCX_VALIDATE= 0x200000

GCL_STYLE = -26

def GET_XY_LPARAM(lParam):
    x = LOWORD(lParam)
    if x > 32768:
        x = x - 65536
    y = HIWORD(lParam)
    return x, y 

FCONTROL = 8
FVIRTKEY = 1

GetModuleHandle = windll.kernel32.GetModuleHandleA
PostQuitMessage= windll.user32.PostQuitMessage
DefWindowProc = windll.user32.DefWindowProcA
CallWindowProc = windll.user32.CallWindowProcA
GetDCEx = windll.user32.GetDCEx
ReleaseDC = windll.user32.ReleaseDC
LoadIcon = windll.user32.LoadIconA
DestroyIcon = windll.user32.DestroyIcon
LoadCursor = windll.user32.LoadCursorA
LoadCursor.restype = ValidHandle
LoadImage = windll.user32.LoadImageA
LoadImage.restype = ValidHandle

RegisterClassEx = windll.user32.RegisterClassExA
SetCursor = windll.user32.SetCursor

CreateWindowEx = windll.user32.CreateWindowExA
CreateWindowEx.restype = ValidHandle

ShowWindow = windll.user32.ShowWindow
UpdateWindow = windll.user32.UpdateWindow
GetMessage = windll.user32.GetMessageA
TranslateMessage = windll.user32.TranslateMessage
DispatchMessage = windll.user32.DispatchMessageA
GetWindowRect = windll.user32.GetWindowRect
MoveWindow = windll.user32.MoveWindow
DestroyWindow = windll.user32.DestroyWindow
CreateMenu = windll.user32.CreateMenu
CreatePopupMenu = windll.user32.CreatePopupMenu
DestroyMenu = windll.user32.DestroyMenu
AppendMenu = windll.user32.AppendMenuA
EnableMenuItem = windll.user32.EnableMenuItem
InitCommonControlsEx = windll.comctl32.InitCommonControlsEx
SendMessage = windll.user32.SendMessageA
PostMessage = windll.user32.PostMessageA
GetClientRect = windll.user32.GetClientRect
GetWindowRect = windll.user32.GetWindowRect
IsDialogMessage = windll.user32.IsDialogMessage
RegisterWindowMessage = windll.user32.RegisterWindowMessageA
GetParent = windll.user32.GetParent
SetWindowLong = windll.user32.SetWindowLongA
SetClassLong = windll.user32.SetClassLongA
GetClassLong = windll.user32.GetClassLongA
SetWindowPos = windll.user32.SetWindowPos
InvalidateRect = windll.user32.InvalidateRect
BeginPaint = windll.user32.BeginPaint
EndPaint = windll.user32.EndPaint
SetCapture = windll.user32.SetCapture
GetCapture = windll.user32.GetCapture
ReleaseCapture = windll.user32.ReleaseCapture
ScreenToClient = windll.user32.ScreenToClient
GetMessagePos = windll.user32.GetMessagePos
BeginDeferWindowPos = windll.user32.BeginDeferWindowPos
DeferWindowPos = windll.user32.DeferWindowPos
EndDeferWindowPos = windll.user32.EndDeferWindowPos
CreateAcceleratorTable = windll.user32.CreateAcceleratorTableA
DestroyAcceleratorTable = windll.user32.DestroyAcceleratorTable
TranslateAccelerator = windll.user32.TranslateAccelerator
ImageList_Create = windll.comctl32.ImageList_Create
ImageList_Destroy = windll.comctl32.ImageList_Destroy
ImageList_AddMasked = windll.comctl32.ImageList_AddMasked

