from ctypes import windll, cdll, Structure, pointer, WinError, CFunction, sizeof

#TODO: auto unicode selection,
#if unicode:
#  CreateWindowEx = windll.user32.CreateWindowExW
#else:
#  CreateWindowEx = windll.user32.CreateWindowExA
#etc, etc

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

class RECT(Structure):
    _fields_ = [("left", "I"),
                ("top", "I"),
                ("right", "I"),
                ("bottom", "I")]
    
class MSG(Structure):
    _fields_ = [("hWnd", "I"),
                ("message", "I"),
                ("wParam", "I"),
                ("lParam", "I"),
                ("time", "I"),
                ("pt", POINT)]

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
                ("fMask", "I"),
                ("fStyle", "I"),
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
                ("iString", "z")]
    
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
WM_DESTROY = 2
CS_HREDRAW = 2
CS_VREDRAW = 1
WHITE_BRUSH = 0

WM_SIZE = 5

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

WM_NCCREATE = 129
WM_NCDESTROY = 130

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

STATUSCLASSNAME = "msctls_statusbar32"

REBARCLASSNAMEW = u"ReBarWindow32"
REBARCLASSNAMEA = "ReBarWindow32"
REBARCLASSNAME = REBARCLASSNAMEA

WC_COMBOBOXEXW = u"ComboBoxEx32"
WC_COMBOBOXEXA = "ComboBoxEx32"
WC_COMBOBOXEX = WC_COMBOBOXEXA

TOOLBARCLASSNAMEW = u"ToolbarWindow32"
TOOLBARCLASSNAMEA = "ToolbarWindow32"
TOOLBARCLASSNAME = TOOLBARCLASSNAMEA
    
CBS_DROPDOWN = 2
MF_STRING = 0

ICC_COOL_CLASSES = 1024
ICC_USEREX_CLASSES = 512

WM_USER = 1024
RB_SETBARINFO = WM_USER + 4

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

TB_BUTTONSTRUCTSIZE = WM_USER+30
TB_ADDBUTTONS       = WM_USER+20

I_IMAGENONE = -2
TBSTATE_ENABLED = 4

BTNS_SHOWTEXT = 0x00000040
CW_USEDEFAULT = 0x80000000

GetModuleHandle = windll.kernel32.GetModuleHandleA
PostQuitMessage= windll.user32.PostQuitMessage
DefWindowProc = windll.user32.DefWindowProcA
GetStockObject = windll.gdi32.GetStockObject
LoadIcon = windll.user32.LoadIconA
LoadCursor = windll.user32.LoadCursorA
RegisterClassEx = windll.user32.RegisterClassExA

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
DestroyMenu = windll.user32.DestroyMenu
AppendMenu = windll.user32.AppendMenuA
InitCommonControlsEx = windll.comctl32.InitCommonControlsEx
SendMessage = windll.user32.SendMessageA
