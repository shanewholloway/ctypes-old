"""
Based on an idea and sample code from
         Author: Eric Koome
         Email: ekoome@kpmg.co.ke

http://msdn.microsoft.com/library/default.asp?url=/library/en-us/shellcc/platform/Shell/programmersguide/shell_adv/bands.asp

http://msdn.microsoft.com/archive/default.asp?url=/archive/en-us/samples/internet/components/bandobjs/default.asp
"""

import _winreg
from ctypes import windll, cdll, byref, Structure, POINTER
from ctypes import c_void_p, c_int, c_wchar, c_ulong

from ctypes.com import COMObject, CLSCTX_INPROC_SERVER, IUnknown, GUID, STDMETHOD, HRESULT
from ctypes.com.register import Registrar
from ctypes.com.persist import IPersistStream, IPersistStreamInit
from ctypes.com.ole import IOleWindow
from ctypes.com.hresult import *
from ctypes.com.automation import VARIANT

from ctypes.wintypes import BOOL, DWORD, RECT, HWND, POINTL

COLORREF = DWORD

################################################################

class IObjectWithSite(IUnknown):
    _iid_ = GUID("{FC4801A3-2BA9-11CF-A229-00AA003D7352}")
    _methods_ = IUnknown._methods_ + [ 
        (STDMETHOD(HRESULT, "SetSite", POINTER(IUnknown))),
        (STDMETHOD(HRESULT, "GetSite", POINTER(GUID), POINTER(c_void_p)))]

class IDockingWindow(IOleWindow):
    _iid_ = GUID("{012DD920-7B26-11D0-8CA9-00A0C92DBFE8}")
    _methods_ = IOleWindow._methods_+ [
        (STDMETHOD (HRESULT, "ShowDW", BOOL)),
        (STDMETHOD (HRESULT, "CloseDW", DWORD)),
        (STDMETHOD (HRESULT, "ResizeBorderDW", POINTER(RECT), POINTER(IUnknown), BOOL))]

################################################################

DBIM_MINSIZE    = 0x0001
DBIM_MAXSIZE    = 0x0002
DBIM_INTEGRAL   = 0x0004
DBIM_ACTUAL     = 0x0008
DBIM_TITLE      = 0x0010
DBIM_MODEFLAGS  = 0x0020
DBIM_BKCOLOR    = 0x0040

DBIMF_NORMAL            = 0x0000
DBIMF_VARIABLEHEIGHT    = 0x0008
DBIMF_DEBOSSED          = 0x0020
DBIMF_BKCOLOR           = 0x0040

class DESKBANDINFO(Structure):
    _fields_ = [("dwMask", DWORD),
                ("ptMinSize", POINTL),
                ("ptMaxSize", POINTL),
                ("ptIntegral", POINTL),
                ("ptActual", POINTL),
                ("wszTitle", c_wchar * 256),
                ("dwModeFlags", DWORD),
                ("crBkgnd", COLORREF)]


OLECMDID_OPEN              = 1
OLECMDID_NEW               = 2
OLECMDID_SAVE              = 3
OLECMDID_SAVEAS            = 4
OLECMDID_SAVECOPYAS        = 5
OLECMDID_PRINT             = 6
OLECMDID_PRINTPREVIEW      = 7
OLECMDID_PAGESETUP         = 8
OLECMDID_SPELL             = 9
OLECMDID_PROPERTIES        = 10
OLECMDID_CUT               = 11
OLECMDID_COPY              = 12
OLECMDID_PASTE             = 13
OLECMDID_PASTESPECIAL      = 14
OLECMDID_UNDO              = 15
OLECMDID_REDO              = 16
OLECMDID_SELECTALL         = 17
OLECMDID_CLEARSELECTION    = 18
OLECMDID_ZOOM              = 19
OLECMDID_GETZOOMRANGE      = 20
OLECMDID_UPDATECOMMANDS    = 21
OLECMDID_REFRESH           = 22
OLECMDID_STOP              = 23
OLECMDID_HIDETOOLBARS      = 24
OLECMDID_SETPROGRESSMAX    = 25
OLECMDID_SETPROGRESSPOS    = 26
OLECMDID_SETPROGRESSTEXT   = 27
OLECMDID_SETTITLE          = 28
OLECMDID_SETDOWNLOADSTATE  = 29
OLECMDID_STOPDOWNLOAD      = 30

OLECMDF_SUPPORTED    = 1
OLECMDF_ENABLED      = 2
OLECMDF_LATCHED      = 4
OLECMDF_NINCHED      = 8

class OLECMD(Structure):
    _fields_  = [("cmdID", c_ulong), # OLECMDID_*
                 ("cmdf", DWORD)]    # OLECMDF_*

OLECMDTEXTF_NONE      = 0
OLECMDTEXTF_NAME      = 1
OLECMDTEXTF_STATUS    = 2

class OLECMDTEXT(Structure):
    _fields_ = [("cmdtextf", DWORD), # OLECMDTEXT_*
                ("cwActual", c_ulong),
                ("cwBuf", c_ulong),
                ("rgwz", c_wchar * 1)] # XXX Actual size is the value in the cwBuf field

class IOleCommandTarget(IUnknown):
    _iid_ = GUID("{B722BCCB-4E68-101B-A2BC-00AA00404770}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "QueryStatus", POINTER(GUID), c_ulong, POINTER(OLECMD), POINTER(OLECMDTEXT)),
        STDMETHOD(HRESULT, "Exec", POINTER(GUID), DWORD, DWORD, POINTER(VARIANT), POINTER(VARIANT))
        ]

class IDeskBand(IDockingWindow):
    _iid_= GUID("{EB0FE172-1A3A-11D0-89B3-00A0C90A90AC}")
    _methods_=IDockingWindow._methods_ + [
        (STDMETHOD (HRESULT, "GetBandInfo", DWORD, DWORD, POINTER(DESKBANDINFO)))]

DBIF_VIEWMODE_NORMAL         = 0x0000
DBIF_VIEWMODE_VERTICAL       = 0x0001
DBIF_VIEWMODE_FLOATING       = 0x0002
DBIF_VIEWMODE_TRANSPARENT    = 0x0004

################################################################

class ToolBandRegistrar(Registrar):

    def build_table(self):
        HKLM = _winreg.HKEY_LOCAL_MACHINE
        HKCR = _winreg.HKEY_CLASSES_ROOT

        BHO_KEY = ("Software\\Microsoft\\Internet Explorer\\Toolbar\\")

        table = Registrar.build_table(self)
        
        # rootkey, subkey, valuename, value
        table.extend([(HKLM, BHO_KEY, self._reg_clsid_, None),
                      (HKCR,"CLSID\\%s\\" % self._reg_clsid_,
                       "", "Python Tool Band"),
                      (HKCR,"CLSID\\%s\\InProcServer32" % self._reg_clsid_,
                       "ThreadingModel", "Apartment")
                      ])

        return table

# IE seems to crash if we don't implement IOleCommandTarget!

class MyBand(COMObject):
    _reg_clsid_ = "{2BCE5CFB-005C-471A-AE6D-0BAF2E92F5B5}"
    _reg_progid_ = "Python.Toolband"
    _reg_clsctx_ = CLSCTX_INPROC_SERVER
    _com_interfaces_ = [
        IPersistStreamInit,
        IObjectWithSite,
        IDeskBand,
        IOleCommandTarget,
##        IInputObject
        ]

    def _get_registrar(cls):
        return ToolBandRegistrar(cls)
    _get_registrar = classmethod(_get_registrar)

    ################################################################

    def IOleCommandTarget_QueryStatus(self, this, pGroup, cCmds, prgCmds, pCmdText):
        # IOleCommandTarget::QueryStatus
        print "IOleCommandTarget"
        if pGroup:
            print "pGroup", pGroup[0]
        return S_OK

    ################################################################

    def IPersistStreamInit_InitNew(self, this):
        return S_OK

    ################################################################

    m_Site = None

    def IObjectWithSite_SetSite(self, this, punkSite):
        if punkSite:
            self.m_Site = punkSite
            polewindow = POINTER(IOleWindow)()
            punkSite.QueryInterface(byref(IOleWindow._iid_),
                                    byref(polewindow))
            hwndParent = HWND()
            polewindow.GetWindow(byref(hwndParent))
            self.hwndParent = hwndParent.value
            # Register and create window
            import win32con
            self.m_hwnd = windll.user32.CreateWindowExA(0, "button", "button",
                                                        win32con.WS_CHILD,
                                                        0, 0, 0, 0,
                                                        hwndParent,
                                                        0,
                                                        None,
                                                        None)
        else:
            self.m_Site = None
        return S_OK

    ################################################################

    m_hwnd = 0

    def IOleWindow_GetWindow(self, this, phwnd):
        if phwnd:
            phwnd[0] = self.m_hwnd
            return S_OK
        else:
            return E_POINTER

    ################################################################

    def IDockingWindow_CloseDW(self, this, dwReserved):
        self.IDockingWindow_ShowDW(None, False)
        if self.m_hwnd:
            windll.user32.DestroyWindow(self.m_hwnd)
            self.m_hwnd = 0
        return S_OK

    def IDockingWindow_ShowDW(self, this, bShow):
        if self.m_hwnd:
            import win32con
            if bShow:
                windll.user32.ShowWindow(self.m_hwnd, win32con.SW_SHOW)
            else:
                windll.user32.ShowWindow(self.m_hwnd, win32con.SW_HIDE)
        
        return S_OK

    ################################################################

    def IDeskBand_GetBandInfo(self, this, dwBandID, dwViewMode, pdbi):
        if not pdbi:
            return E_INVALIDARG
        dbi = pdbi[0]
        mask = dbi.dwMask

        if mask & DBIM_MINSIZE:
            dbi.ptMinSize.x = 5
            dbi.ptMinSize.y = 5

        if mask & DBIM_MAXSIZE:
            dbi.ptMaxSize.x = -1
            dbi.ptMaxSize.y = -1

        if mask & DBIM_ACTUAL:
            dbi.ptActual.x = 0
            dbi.ptActual.y = 0

        if mask & DBIM_INTEGRAL:
            dbi.ptIntegral.x = 1
            dbi.ptIntegral.y = 1

        if mask & DBIM_TITLE:
            dbi.wszTitle = u"Hello World"

        if mask & DBIM_MODEFLAGS:
            dbi.dwModeFlags = DBIMF_VARIABLEHEIGHT


        if mask & DBIM_BKCOLOR:
            dbi.dwMask &= ~ DBIM_BKCOLOR
        
        return S_OK

################################################################

if __name__ == "__main__":
    from ctypes.com.server import UseCommandLine
    UseCommandLine(MyBand)
