## 	   Copyright (c) 2003 Henk Punt

## Permission is hereby granted, free of charge, to any person obtaining
## a copy of this software and associated documentation files (the
## "Software"), to deal in the Software without restriction, including
## without limitation the rights to use, copy, modify, merge, publish,
## distribute, sublicense, and/or sell copies of the Software, and to
## permit persons to whom the Software is furnished to do so, subject to
## the following conditions:

## The above copyright notice and this permission notice shall be
## included in all copies or substantial portions of the Software.

## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
## EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
## MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
## NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
## LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
## OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
## WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE

from windows import *
from wtl import *

ATL_IDW_BAND_FIRST = 0xEB00
HTREEITEM = HANDLE
HIMAGELIST = HANDLE

UINT_MAX = (1l << 32)

class NMCBEENDEDIT(Structure):
    _fields_ = [("hdr", NMHDR),
                ("fChanged", BOOL),
                ("iNewSelection", INT),
                ("szText", TCHAR),
                ("iWhy", INT)]

class LVCOLUMN(Structure):
    _fields_ = [("mask", UINT),
                ("fmt", INT),
                ("cx", INT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iSubItem", INT),
                ("iImage", INT),
                ("iOrder", INT)]

class LVITEM(Structure):
    _fields_ = [("mask", UINT),
                ("iItem", INT),
                ("iSubItem", INT),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("lParam", LPARAM),
                ("iIndent", INT)]

class TVITEMEX(Structure):
    _fields_ = [("mask", UINT),
                ("hItem", HTREEITEM),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("iSelectedImage", INT),
                ("cChildren", INT),
                ("lParam", LPARAM),
                ("iIntegral", INT)]

class TVITEM(Structure):
    _fields_ = [("mask", UINT),
                ("hItem", HTREEITEM),
                ("state", UINT),
                ("stateMask", UINT),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("iSelectedImage", INT),
                ("cChildren", INT),
                ("lParam", LPARAM)]

class TBBUTTON(Structure):
    _fields_ = [("iBitmap", INT),
                ("idCommand", INT),
                ("fsState", BYTE),
                ("fsStyle", BYTE),
                ("bReserved", BYTE * 2),
                ("dwData", DWORD_PTR),
                ("iString", INT_PTR)]

class TBBUTTONINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("dwMask", DWORD),
                ("idCommand", INT),
                ("iImage", INT),
                ("fsState", BYTE),
                ("fsStyle", BYTE),
                ("cx", WORD),
                ("lParam", DWORD_PTR),
                ("pszText", LPTSTR),
                ("cchText", INT)]

class TVINSERTSTRUCT(Structure):
    _fields_ = [("hParent", HTREEITEM),
                ("hInsertAfter", HTREEITEM),
                ("itemex", TVITEMEX)]

class TCITEM(Structure):
    _fields_ = [("mask", UINT),
                ("dwState", DWORD),
                ("dwStateMask", DWORD),
                ("pszText", LPTSTR),
                ("cchTextMax", INT),
                ("iImage", INT),
                ("lParam", LPARAM)]

class NMTREEVIEW(Structure):
    _fields_ = [("hdr", NMHDR),
                ("action", UINT),
                ("itemOld", TVITEM),
                ("itemNew", TVITEM),
                ("ptDrag", POINT)]
    
class INITCOMMONCONTROLSEX(Structure):
    _fields_ = [("dwSize", DWORD),
                ("dwICC", DWORD)]

class REBARINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("himl", HIMAGELIST)]

class REBARBANDINFO(Structure):
    _fields_ = [("cbSize", UINT),
                ("fMask", UINT),
                ("fStyle", UINT),
                ("clrFore", COLORREF),
                ("clrBack", COLORREF),
                ("lpText", LPTSTR),
                ("cch", UINT),
                ("iImage", INT),
                ("hwndChild", HWND),
                ("cxMinChild", UINT),
                ("cyMinChild", UINT),
                ("cx", UINT),
                ("hbmBack", HBITMAP),
                ("wID", UINT),
                ("cyChild", UINT),
                ("cyMaxChild", UINT),
                ("cyIntegral", UINT),
                ("cxIdeal", UINT),
                ("lParam", LPARAM),
                ("cxHeader", UINT)]

class NMTOOLBAR(Structure):
    _fields_ = [("hdr", NMHDR),
                ("iItem", INT),
                ("tbButton", TBBUTTON),
                ("cchText", INT),
                ("pszText", LPTSTR),
                ("rcButton", RECT)]

class NMTBHOTITEM(Structure):
    _fields_ = [("hdr", NMHDR),
                ("idOld", INT),
                ("idNew", INT),
                ("dwFlags", DWORD)]


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

CCS_NODIVIDER =	64
CCS_NOPARENTALIGN = 8
CCS_NORESIZE = 4
CCS_TOP = 1


CBS_DROPDOWN = 2

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

RBN_FIRST	= ((UINT_MAX) - 831)
RBN_HEIGHTCHANGE = RBN_FIRST

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
TB_PRESSBUTTON       = WM_USER + 3
TB_GETRECT        =      (WM_USER + 51)
TB_SETHOTITEM   =        (WM_USER + 72)
TB_HITTEST     =         (WM_USER + 69)
TB_GETHOTITEM  =         (WM_USER + 71)

TVIF_TEXT    = 1
TVIF_IMAGE   =2
TVIF_PARAM   =4
TVIF_STATE   =8
TVIF_HANDLE = 16
TVIF_SELECTEDIMAGE  = 32
TVIF_CHILDREN      =  64
TVIF_INTEGRAL      =  0x0080
TVIF_DI_SETITEM    =  0x1000
 
TVI_ROOT     = 0xFFFF0000l
TVI_FIRST    = 0xFFFF0001l
TVI_LAST     = 0xFFFF0002l
TVI_SORT     = 0xFFFF0003l

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

CBEN_FIRST  =  (UINT_MAX) - 800
CBEN_ENDEDITA = CBEN_FIRST - 5
CBEN_ENDEDITW = CBEN_FIRST - 6
CBEN_ENDEDIT = CBEN_ENDEDITA

STATUSCLASSNAME = "msctls_statusbar32"

REBARCLASSNAMEW = u"ReBarWindow32"
REBARCLASSNAMEA = "ReBarWindow32"
REBARCLASSNAME = REBARCLASSNAMEA

WC_COMBOBOXEXW = u"ComboBoxEx32"
WC_COMBOBOXEXA = "ComboBoxEx32"
WC_COMBOBOXEX = WC_COMBOBOXEXA

WC_TREEVIEWA = "SysTreeView32"
WC_TREEVIEWW = u"SysTreeView32"
WC_TREEVIEW = WC_TREEVIEWA

WC_LISTVIEWA = "SysListView32"
WC_LISTVIEWW = u"SysListView32"
WC_LISTVIEW = WC_LISTVIEWA

TOOLBARCLASSNAMEW = u"ToolbarWindow32"
TOOLBARCLASSNAMEA = "ToolbarWindow32"
TOOLBARCLASSNAME = TOOLBARCLASSNAMEA

WC_TABCONTROLA =    "SysTabControl32"
WC_TABCONTROLW =      u"SysTabControl32"
WC_TABCONTROL = WC_TABCONTROLA

LVS_ICON    = 0
LVS_REPORT   =1
LVS_SMALLICON =       2
LVS_LIST    = 3
LVS_TYPEMASK= 3
LVS_SINGLESEL=        4
LVS_SHOWSELALWAYS=    8
LVS_SORTASCENDING =   16
LVS_SORTDESCENDING =  32
LVS_SHAREIMAGELISTS = 64
LVS_NOLABELWRAP     = 128
LVS_AUTOARRANGE     = 256
LVS_EDITLABELS      = 512
LVS_NOSCROLL= 0x2000
LVS_TYPESTYLEMASK  =  0xfc00
LVS_ALIGNTOP= 0
LVS_ALIGNLEFT =       0x800
LVS_ALIGNMASK  =      0xc00
LVS_OWNERDRAWFIXED=   0x400
LVS_NOCOLUMNHEADER =  0x4000
LVS_NOSORTHEADER   =  0x8000
LVS_OWNERDATA =4096
LVS_EX_CHECKBOXES= 4
LVS_EX_FULLROWSELECT= 32
LVS_EX_GRIDLINES =1
LVS_EX_HEADERDRAGDROP= 16
LVS_EX_ONECLICKACTIVATE= 64
LVS_EX_SUBITEMIMAGES= 2
LVS_EX_TRACKSELECT= 8
LVS_EX_TWOCLICKACTIVATE= 128
LVS_EX_FLATSB       = 0x00000100
LVS_EX_REGIONAL     = 0x00000200
LVS_EX_INFOTIP      = 0x00000400
LVS_EX_UNDERLINEHOT = 0x00000800
LVS_EX_UNDERLINECOLD= 0x00001000
LVS_EX_MULTIWORKAREAS =       0x00002000
LVS_EX_LABELTIP     = 0x00004000
LVS_EX_BORDERSELECT = 0x00008000


LVM_FIRST = 0x1000
LVM_INSERTCOLUMNA = (LVM_FIRST+27)
LVM_INSERTCOLUMN = LVM_INSERTCOLUMNA
LVM_INSERTITEMA = (LVM_FIRST+7)
LVM_SETITEMA = (LVM_FIRST+6)
LVM_INSERTITEM = LVM_INSERTITEMA

LVM_SETITEM = LVM_SETITEMA

LVCF_FMT     =1
LVCF_WIDTH   =2
LVCF_TEXT    =4
LVCF_SUBITEM =8
LVCF_IMAGE= 16
LVCF_ORDER= 32
LVCFMT_LEFT = 0
LVCFMT_RIGHT= 1
LVCFMT_CENTER   =     2
LVCFMT_JUSTIFYMASK =  3
LVCFMT_BITMAP_ON_RIGHT =4096
LVCFMT_COL_HAS_IMAGES = 32768
LVCFMT_IMAGE =2048

LVIF_TEXT   = 1
LVIF_IMAGE  = 2
LVIF_PARAM  = 4
LVIF_STATE  = 8
LVIF_DI_SETITEM =  0x1000

ICC_LISTVIEW_CLASSES =1
ICC_TREEVIEW_CLASSES =2
ICC_BAR_CLASSES      =4
ICC_TAB_CLASSES      =8
ICC_UPDOWN_CLASS =16
ICC_PROGRESS_CLASS =32
ICC_HOTKEY_CLASS =64
ICC_ANIMATE_CLASS= 128
ICC_WIN95_CLASSES= 255
ICC_DATE_CLASSES =256
ICC_USEREX_CLASSES =512
ICC_COOL_CLASSES =1024
ICC_INTERNET_CLASSES =2048
ICC_PAGESCROLLER_CLASS =4096
ICC_NATIVEFNTCTL_CLASS= 8192

TCN_FIRST  =  (UINT_MAX) -550
TCN_LAST   =  (UINT_MAX) -580
TCN_KEYDOWN   =  TCN_FIRST
TCN_SELCHANGE =        (TCN_FIRST-1)
TCN_SELCHANGING  =     (TCN_FIRST-2)

TCM_FIRST   = 0x1300
TCM_INSERTITEMA  =    (TCM_FIRST+7)
TCM_INSERTITEMW  =   (TCM_FIRST+62)
TCM_INSERTITEM = TCM_INSERTITEMA
TCM_ADJUSTRECT = (TCM_FIRST+40)
TCM_GETCURSEL   =     (TCM_FIRST+11)
TCM_SETCURSEL   =     (TCM_FIRST+12)
TCM_GETITEMA = (TCM_FIRST+5)
TCM_GETITEMW = (TCM_FIRST+60)
TCM_GETITEM = TCM_GETITEMA

TVN_FIRST  =  ((UINT_MAX)-400)
TVN_LAST   =  ((UINT_MAX)-499)
TVN_ITEMEXPANDINGA =  (TVN_FIRST-5)
TVN_ITEMEXPANDINGW =  (TVN_FIRST-54)
TVN_ITEMEXPANDING = TVN_ITEMEXPANDINGA
TVN_SELCHANGEDA  =    (TVN_FIRST-2)
TVN_SELCHANGEDW  =    (TVN_FIRST-51)
TVN_SELCHANGED  =  TVN_SELCHANGEDA

SB_SIMPLE =   (WM_USER+9)
SB_SETTEXTA = (WM_USER+1)
SB_SETTEXTW = (WM_USER+11)
SB_SETTEXT = SB_SETTEXTA

SBT_OWNERDRAW   =     0x1000
SBT_NOBORDERS   =     256
SBT_POPOUT   = 512
SBT_RTLREADING =      1024
SBT_OWNERDRAW  =      0x1000
SBT_NOBORDERS  =      256
SBT_POPOUT   = 512
SBT_RTLREADING = 1024
SBT_TOOLTIPS = 0x0800

TBN_FIRST          =  ((UINT_MAX)-700)
TBN_DROPDOWN       =     (TBN_FIRST - 10)
TBN_HOTITEMCHANGE  =  (TBN_FIRST - 13)
TBDDRET_DEFAULT       =  0
TBDDRET_NODEFAULT     =  1
TBDDRET_TREATPRESSED  =  2

ImageList_Create = windll.comctl32.ImageList_Create
ImageList_Destroy = windll.comctl32.ImageList_Destroy
ImageList_AddMasked = windll.comctl32.ImageList_AddMasked
ImageList_AddIcon = windll.comctl32.ImageList_AddIcon
ImageList_SetBkColor = windll.comctl32.ImageList_SetBkColor

InitCommonControlsEx = windll.comctl32.InitCommonControlsEx


class StatusBar(Window):
    _class_ = STATUSCLASSNAME
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | SBS_SIZEGRIP

    def Simple(self, fSimple):
        SendMessage(self.handle, SB_SIMPLE, fSimple, 0)

    def SetText(self, txt):
        SendMessage(self.handle, SB_SETTEXT, (255 | SBT_NOBORDERS), txt)
        
class ComboBox(Window):
    _class_ = WC_COMBOBOXEX
    _class_ws_style_ = WS_VISIBLE | WS_CHILD | CBS_DROPDOWN

class TabControl(Window):
    _class_ = WC_TABCONTROL
    _class_ws_style_ = WS_VISIBLE | WS_CHILD | TCS_MULTILINE

    def InsertItem(self, iItem, item):        
        return SendMessage(self.handle, TCM_INSERTITEM, iItem, byref(item))

    def GetItem(self, index, mask):
        item = TCITEM()
        item.mask = mask
        if SendMessage(self.handle, TCM_GETITEM, index, byref(item)):
            return item
        else:
            raise "error"
        


    def AdjustRect(self, fLarger, rect):
        lprect = byref(rect)
        SendMessage(self.handle, TCM_ADJUSTRECT, fLarger, lprect)

    def GetCurSel(self):
        return SendMessage(self.handle, TCM_GETCURSEL, 0, 0)
    
class TreeView(Window):
    _class_ = WC_TREEVIEW
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | WS_TABSTOP |\
                       TVS_HASBUTTONS|TVS_LINESATROOT|TVS_HASLINES
    _class_ws_ex_style_ = 0

    def InsertItem(self, hParent, hInsertAfter, s, iImage, iSelectedImage):
        itemEx = TVITEMEX()
        itemEx.mask  = TVIF_TEXT | TVIF_IMAGE | TVIF_SELECTEDIMAGE
        itemEx.pszText = s
        itemEx.iImage = iImage
        itemEx.iSelectedImage = iSelectedImage
        
        insertStruct = TVINSERTSTRUCT()
        insertStruct.hParent = hParent
        insertStruct.hInsertAfter = hInsertAfter
        insertStruct.itemex = itemEx
        
        return SendMessage(self.handle, TVM_INSERTITEM, 0, byref(insertStruct))

    def SetImageList(self, imageList, iImage = TVSIL_NORMAL):
        return SendMessage(self.handle, TVM_SETIMAGELIST, iImage, handle(imageList))

class ListView(Window):
    _class_ = WC_LISTVIEW
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | LVS_REPORT 
    _class_ws_ex_style_ = 0

    def InsertColumn(self, iCol, lvcolumn):
        return SendMessage(self.handle, LVM_INSERTCOLUMN, iCol, byref(lvcolumn))
    
    def InsertItem(self, item):
        return SendMessage(self.handle, LVM_INSERTITEM, 0, byref(item))

    def SetItem(self, item):
        return SendMessage(self.handle, LVM_SETITEM, 0, byref(item))

class ToolBar(Window):
    _class_ = TOOLBARCLASSNAME
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN | WS_CLIPSIBLINGS | CCS_NODIVIDER |\
                       CCS_NORESIZE | CCS_NOPARENTALIGN | TBSTYLE_FLAT | TBSTYLE_LIST

    def __init__(self, *args, **kwargs):
        apply(Window.__init__, (self,) + args, kwargs)        

    def PressButton(self, idButton, fPress):
        SendMessage(self.handle, TB_PRESSBUTTON, idButton, fPress)

    def GetRect(self, idCtrl):
        rc = RECT()
        SendMessage(self.handle, TB_GETRECT, idCtrl, byref(rc))
        return rc

    def HitTest(self, pt):
        return SendMessage(self.handle, TB_HITTEST, 0, byref(pt))
        
    def SetHotItem(self, idButton):
        SendMessage(self.handle, TB_SETHOTITEM, idButton, 0)

    def GetHotItem(self):
        return SendMessage(self.handle, TB_GETHOTITEM, 0, 0)
        
class Rebar(Window):
    _class_ = REBARCLASSNAME
    _class_ws_style_ = WS_CHILDWINDOW|WS_VISIBLE|WS_CLIPSIBLINGS|WS_CLIPCHILDREN|WS_BORDER|\
                       RBS_VARHEIGHT|RBS_BANDBORDERS|RBS_AUTOSIZE|RBS_DBLCLKTOGGLE|\
                       RBS_REGISTERDROP|CCS_NODIVIDER|CCS_TOP|CCS_NOPARENTALIGN
    _class_ws_ex_style_ = WS_EX_LEFT|WS_EX_LTRREADING|WS_EX_RIGHTSCROLLBAR|WS_EX_TOOLWINDOW

    def __init__(self, *args, **kwargs):
        apply(Window.__init__, (self,) + args, kwargs)
        
        rebarInfo = REBARINFO()
        rebarInfo.cbSize = sizeof(REBARINFO)
        rebarInfo.fMask = 0
        rebarInfo.himl = NULL
        SendMessage(self.handle, RB_SETBARINFO, 0, byref(rebarInfo))

class ImageList(disposable):
    def __init__(self, cx, cy, flags, cInitial, cGrow):
        disposable.__init__(self,
                            ImageList_Create(cx, cy, flags, cInitial, cGrow))

    def __dispose__(self):
        ImageList_Destroy(self.handle)
        
    def AddMasked(self, bitmap, crMask):
        return ImageList_AddMasked(self.handle, handle(bitmap), crMask)

    def SetBkColor(self, clrRef):
        ImageList_SetBkColor(self.handle, clrRef)
        
    def AddIcon(self, hIcon):
        return ImageList_AddIcon(self.handle, hIcon)

    def AddIconsFromModule(self, moduleName, cx, cy, uFlags):
        hdll = GetModuleHandle(moduleName)
        i = 1
        while 1:
            try:
                hIcon = LoadImage(hdll, i , IMAGE_ICON, cx, cy, uFlags)
                self.AddIcon(hIcon)
            except:
                break
            i += 1

        
def InitCommonControls(dwICC):
    iccex = INITCOMMONCONTROLSEX()
    iccex.dwSize = sizeof(INITCOMMONCONTROLSEX)
    iccex.dwICC = dwICC
    InitCommonControlsEx(byref(iccex))
