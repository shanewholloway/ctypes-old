from windows import *
from wtl import *
from ctypes import c_int, c_uint, c_char, c_char_p

ATL_IDW_BAND_FIRST = 0xEB00
UINT = 1l << 32

class NMCBEENDEDIT(Structure):
    _fields_ = [("hdr", NMHDR),
                ("fChanged", c_int),
                ("iNewSelection", c_int),
                ("szText", c_char * 260),
                ("iWhy", c_int)]

class LVCOLUMN(Structure):
    _fields_ = [("mask", c_uint),
                ("fmt", c_int),
                ("cx", c_int),
                ("pszText", c_char_p),
                ("cchTextMax", c_int),
                ("iSubItem", c_int),
                ("iImage", c_int),
                ("iOrder", c_int)]

class LVITEM(Structure):
    _fields_ = [("mask", c_uint),
                ("iItem", c_int),
                ("iSubItem", c_int),
                ("state", c_uint),
                ("stateMask", c_uint),
                ("pszText", c_char_p),
                ("cchTextMax", c_int),
                ("iImage", c_int),
                ("lParam", c_uint),
                ("iIndent", c_int)]
##if (_WIN32_IE >= 0x560)
#    int iGroupId;
#    UINT cColumns; // tile view columns
#    PUINT puColumns;
#endif
#} LVITEM, *LPLVITEM; 


CBEN_FIRST  =  (1l << 32) - 800
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

TCN_FIRST  =  (1l << 32) -550
TCN_LAST   =  (1l << 32) -580
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

TVN_FIRST  =  ((UINT)-400)
TVN_LAST   =  ((UINT)-499)
TVN_ITEMEXPANDINGA =  (TVN_FIRST-5)
TVN_ITEMEXPANDINGW =  (TVN_FIRST-54)
TVN_ITEMEXPANDING = TVN_ITEMEXPANDINGA

class StatusBar(Window):
    _class_ = STATUSCLASSNAME
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | SBS_SIZEGRIP
    
class ComboBox(Window):
    _class_ = WC_COMBOBOXEX
    _class_ws_style_ = WS_VISIBLE | WS_CHILD | CBS_DROPDOWN

class TabControl(Window):
    _class_ = WC_TABCONTROL
    _class_ws_style_ = WS_VISIBLE | WS_CHILD | TCS_MULTILINE

    def InsertItem(self, iItem, item):        
        return SendMessage(self.handle, TCM_INSERTITEM, iItem, pointer(item))

    def GetItem(self, index, mask):
        item = TCITEM()
        item.mask = mask
        if SendMessage(self.handle, TCM_GETITEM, index, pointer(item)):
            return item
        else:
            raise "error"
        


    def AdjustRect(self, fLarger, rect):
        lprect = pointer(rect)
        SendMessage(self.handle, TCM_ADJUSTRECT, fLarger, lprect)

    def GetCurSel(self):
        return SendMessage(self.handle, TCM_GETCURSEL, 0, 0)
    
class TreeView(Window):
    _class_ = WC_TREEVIEW
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | WS_TABSTOP |\
                       TVS_HASBUTTONS|TVS_LINESATROOT|TVS_HASLINES
    _class_ws_ex_style_ = 0

    def InsertItem(self, hParent, hInsertAfter, s):
        itemEx = TVITEMEX()
        itemEx.mask  = TVIF_TEXT
        itemEx.pszText = s

        insertStruct = TVINSERTSTRUCT()
        insertStruct.hParent = hParent
        insertStruct.hInsertAfter = hInsertAfter
        insertStruct.itemex = itemEx
        
        return SendMessage(self.handle, TVM_INSERTITEM, 0, pointer(insertStruct))

    def SetImageList(self, imageList, iImage = TVSIL_NORMAL):
        return SendMessage(self.handle, TVM_SETIMAGELIST, iImage, handle(imageList))

class ListView(Window):
    _class_ = WC_LISTVIEW
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | LVS_REPORT 
    _class_ws_ex_style_ = 0

    def InsertColumn(self, iCol, lvcolumn):
        return SendMessage(self.handle, LVM_INSERTCOLUMN, iCol, pointer(lvcolumn))
    
    def InsertItem(self, item):
        return SendMessage(self.handle, LVM_INSERTITEM, 0, pointer(item))

    def SetItem(self, item):
        return SendMessage(self.handle, LVM_SETITEM, 0, pointer(item))
    
class CommandBar(Window):
    _class_ = TOOLBARCLASSNAME
    _class_ws_style_ = WS_CHILD | WS_VISIBLE | WS_CLIPCHILDREN | WS_CLIPSIBLINGS | CCS_NODIVIDER |\
                  CCS_NORESIZE | CCS_NOPARENTALIGN | TBSTYLE_FLAT | TBSTYLE_LIST

    def __init__(self, *args, **kwargs):
        apply(Window.__init__, (self,) + args, kwargs)        
        SendMessage(self.handle, TB_BUTTONSTRUCTSIZE, sizeof(TBBUTTON), 0)
        SendMessage(self.handle, TB_SETIMAGELIST, 0, 0)
        self.ShowKeyboardCues(FALSE)

    def ShowKeyboardCues(self, bShow):
        if bShow:
            SendMessage(self.handle, TB_SETDRAWTEXTFLAGS, DT_HIDEPREFIX, 0)
        else:
            SendMessage(self.handle, TB_SETDRAWTEXTFLAGS, DT_HIDEPREFIX, DT_HIDEPREFIX)
            
        self.Invalidate()
        self.UpdateWindow()

    def AttachMenu(self, menus):
        idc = 0

        self.SetRedraw(FALSE)
        
        for menu in menus:
            tbButt = TBBUTTON()
            tbButt.iBitmap = 0
            tbButt.idCommand = idc
            tbButt.fsState = TBSTATE_ENABLED
            tbButt.fsStyle = TBSTYLE_BUTTON | TBSTYLE_AUTOSIZE | TBSTYLE_DROPDOWN
            tbButt.dwData = 0
            tbButt.iString = 0

            SendMessage(self.handle, TB_INSERTBUTTON, -1, pointer(tbButt))

            bi = TBBUTTONINFO()
            bi.cbSize = sizeof(TBBUTTONINFO)
            bi.dwMask = TBIF_TEXT
            bi.pszText = menu

            SendMessage(self.handle, TB_SETBUTTONINFO, idc, pointer(bi))

            idc += 1

        self.SetRedraw(TRUE)
        self.Invalidate()
        self.UpdateWindow()

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
        SendMessage(self.handle, RB_SETBARINFO, 0, pointer(rebarInfo))
        

    def AddSimpleReBarBandCtrl(self, ctrl, nID = 0, title = NULL, bNewRow = FALSE,
                               cxWidth = 0, bFullWidthAlways = FALSE):

        hWndBand = ctrl.handle

        #Get number of buttons on the toolbar
        nBtnCount = SendMessage(hWndBand, TB_BUTTONCOUNT, 0, 0)

        #Set band info structure
        rbBand = REBARBANDINFO()
        rbBand.cbSize = sizeof(REBARBANDINFO)

        if WIN32_IE >= 0x0400:
            rbBand.fMask = RBBIM_CHILD | RBBIM_CHILDSIZE | RBBIM_STYLE | RBBIM_ID | RBBIM_SIZE\
                           | RBBIM_IDEALSIZE
        else:
            rbBand.fMask = RBBIM_CHILD | RBBIM_CHILDSIZE | RBBIM_STYLE | RBBIM_ID | RBBIM_SIZE

        if title != NULL:
            rbBand.fMask |= RBBIM_TEXT

        rbBand.fStyle = RBBS_CHILDEDGE

        if WIN32_IE >= 0x0500 and nBtnCount > 0:
            # add chevron style for toolbar with buttons
            #rbBand.fStyle |= RBBS_USECHEVRON
            #TODO find RBBS_USECHEVRON constant
            pass        

        if bNewRow:
            rbBand.fStyle |= RBBS_BREAK

        if title != NULL:
            rbBand.lpText = title
            
        rbBand.hwndChild = hWndBand
        
        if nID == 0: # calc band ID
            nID = ATL_IDW_BAND_FIRST + SendMessage(self.handle, RB_GETBANDCOUNT, 0, 0)

        rbBand.wID = nID

        rcTmp = RECT()
        if nBtnCount > 0:
            bRet = SendMessage(hWndBand, TB_GETITEMRECT, nBtnCount - 1, pointer(rcTmp))
            if cxWidth != 0:
                rbBand.cx = cxWidth
            else:
                rbBand.cx = rcTmp.right
            rbBand.cyMinChild = rcTmp.bottom - rcTmp.top
            if bFullWidthAlways:
                rbBand.cxMinChild = rbBand.cx
            elif title == 0:
                SendMessage(hWndBand, TB_GETITEMRECT, 0, pointer(rcTmp))
                rbBand.cxMinChild = rcTmp.right
            else:
                rbBand.cxMinChild = 0
        else: #	// no buttons, either not a toolbar or really has no buttons
            GetWindowRect(hWndBand, pointer(rcTmp))
            if cxWidth != 0:
               rbBand.cx = cxWidth
            else:
                rbBand.cx = rcTmp.right - rcTmp.left

            if bFullWidthAlways:
                rbBand.cxMinChild = rbBand.cx
            else:
                rbBand.cxMinChild = 0
                
            rbBand.cyMinChild = rcTmp.bottom - rcTmp.top

        if WIN32_IE >= 0x0400:
            rbBand.cxIdeal = rbBand.cx;
            
        #Add the band
        SendMessage(self.handle, RB_INSERTBAND, -1, pointer(rbBand))

        #if WIN32_IE >= 0x0501:
        #    exStyle = SendMessage(hWndBand, TB_GETEXTENDEDSTYLE, 0, 0)
        #    SendMessage(hWndBand, TB_SETEXTENDEDSTYLE, 0, dwExStyle | \
        #                TBSTYLE_EX_HIDECLIPPEDBUTTONS)


class ImageList(disposable):
    def __init__(self, cx, cy, flags, cInitial, cGrow):
        disposable.__init__(self,
                            ImageList_Create(cx, cy, flags, cInitial, cGrow))

    def __dispose__(self):
        ImageList_Destroy(self.handle)
        
    def AddMasked(self, bitmap, crMask):
        return ImageList_AddMasked(self.handle, handle(bitmap), crMask)

    
        
def InitCommonControls(dwICC):
    iccex = INITCOMMONCONTROLSEX()
    iccex.dwSize = sizeof(INITCOMMONCONTROLSEX)
    iccex.dwICC = dwICC
    InitCommonControlsEx(pointer(iccex))
