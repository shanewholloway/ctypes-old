# -*- python -*-
# Generated from c:\windows\system32\shdocvw.dll

# NOTE: This is a GENERATED file. Please do not make changes,
# they will probably be overwritten next time it is regenerated.

from ctypes.com import IUnknown, GUID, STDMETHOD, HRESULT
from ctypes.com.automation import IDispatch, BSTR, VARIANT

from ctypes import POINTER, c_voidp, c_byte, c_ubyte, \
     c_short, c_ushort, c_int, c_uint, c_long, c_ulong, \
     c_float, c_double, Structure, byref, sizeof

class COMObject:
    # later this class will be used to create COM objects.
    pass

class enum(c_int):
    pass

OLECMDID = enum
OLECMDEXECOPT = enum

class dispinterface(IDispatch):
    class __metaclass__(type(IDispatch)):
        def __setattr__(self, name, value):
            if name == '_dispmethods_':
##                protos = []
                dispmap = {}
                for dispid, mthname, proto in value:
##                    protos.append(proto)
                    dispmap[dispid] = mthname
##                setattr(self, '_methods_', IDispatch._methods_ + protos)
                setattr(self, '_methods_', IDispatch._methods_)
                type(IDispatch).__setattr__(self, '_dispmap_', dispmap)
            type(IDispatch).__setattr__(self, name, value)

def DISPMETHOD(dispid, restype, name, *argtypes):
    return dispid, name, STDMETHOD(HRESULT, name, *argtypes)

##############################################################################

# The Type Library
class SHDocVw:
    'Microsoft Internet Controls'
    guid = GUID('{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}')
    version = (1, 1)
    flags = 0x8
    path = 'c:\\windows\\system32\\shdocvw.dll'

##############################################################################

class ShellWindowFindWindowOptions(enum):
    """Options for ShellWindows FindWindow"""
    _iid_ = GUID('{7716A370-38CA-11D0-A48B-00A0C90A8F39}')
    SWFO_NEEDDISPATCH = 1
    SWFO_INCLUDEPENDING = 2
    SWFO_COOKIEPASSED = 4


class ShellWindowTypeConstants(enum):
    """Constants for ShellWindows registration"""
    _iid_ = GUID('{F41E6981-28E5-11D0-82B4-00A0C90C29C5}')
    SWC_EXPLORER = 0
    SWC_BROWSER = 1
    SWC_3RDPARTY = 2
    SWC_CALLBACK = 4


class CommandStateChangeConstants(enum):
    """Constants for WebBrowser CommandStateChange"""
    _iid_ = GUID('{34A226E0-DF30-11CF-89A9-00A0C9054129}')
    CSC_UPDATECOMMANDS = -1
    CSC_NAVIGATEFORWARD = 1
    CSC_NAVIGATEBACK = 2


class SecureLockIconConstants(enum):
    """Constants for WebBrowser security icon notification"""
    _iid_ = GUID('{65507BE0-91A8-11D3-A845-009027220E6D}')
    secureLockIconUnsecure = 0
    secureLockIconMixed = 1
    secureLockIconSecureUnknownBits = 2
    secureLockIconSecure40Bit = 3
    secureLockIconSecure56Bit = 4
    secureLockIconSecureFortezza = 5
    secureLockIconSecure128Bit = 6


class tagREADYSTATE(enum):
    READYSTATE_UNINITIALIZED = 0
    READYSTATE_LOADING = 1
    READYSTATE_LOADED = 2
    READYSTATE_INTERACTIVE = 3
    READYSTATE_COMPLETE = 4


##############################################################################

class IWebBrowser2(IDispatch):
    """Web Browser Interface for IE4."""
    _iid_ = GUID('{D30C1661-CDAF-11D0-8A3E-00C04FC9E26E}')


class IShellWindows(IDispatch):
    """Definition of interface IShellWindows"""
    _iid_ = GUID('{85CB6900-4D95-11CF-960C-0080C7F4EE85}')


class IWebBrowser(IDispatch):
    """Web Browser interface"""
    _iid_ = GUID('{EAB22AC1-30C1-11CF-A7EB-0000C05BAE0B}')


class ISearchAssistantOC(IDispatch):
    """ISearchAssistantOC Interface"""
    _iid_ = GUID('{72423E8F-8011-11D2-BE79-00A0C9A83DA1}')


class ISearches(IDispatch):
    """Searches Enum"""
    _iid_ = GUID('{47C922A2-3DD5-11D2-BF8B-00C04FB93661}')


class DWebBrowserEvents(dispinterface):
    """Web Browser Control Events (old)"""
    _iid_ = GUID('{EAB22AC2-30C1-11CF-A7EB-0000C05BAE0B}')


class ISearchAssistantOC3(IDispatch):
    """ISearchAssistantOC3 Interface"""
    _iid_ = GUID('{72423E8F-8011-11D2-BE79-00A0C9A83DA3}')


class IWebBrowserApp(IDispatch):
    """Web Browser Application Interface."""
    _iid_ = GUID('{0002DF05-0000-0000-C000-000000000046}')


class DWebBrowserEvents2(dispinterface):
    """Web Browser Control events interface"""
    _iid_ = GUID('{34A715A0-6587-11D0-924A-0020AFC7AC4D}')


class DShellWindowsEvents(dispinterface):
    """Event interface for IShellWindows"""
    _iid_ = GUID('{FE4106E0-399A-11D0-A48C-00A0C90A8F39}')


class ISearchAssistantOC2(IDispatch):
    """ISearchAssistantOC2 Interface"""
    _iid_ = GUID('{72423E8F-8011-11D2-BE79-00A0C9A83DA2}')


class ISearch(IDispatch):
    """Enumerated Search"""
    _iid_ = GUID('{BA9239A4-3DD5-11D2-BF8B-00C04FB93661}')


class IShellUIHelper(IDispatch):
    """Shell UI Helper Control Interface"""
    _iid_ = GUID('{729FE2F8-1EA8-11D1-8F85-00C04FC2FBE1}')


class DShellNameSpaceEvents(dispinterface):
    _iid_ = GUID('{55136806-B2DE-11D1-B9F2-00A0C98BC547}')


class IShellNameSpace(IDispatch):
    """IShellNameSpace Interface"""
    _iid_ = GUID('{E572D3C9-37BE-4AE2-825D-D521763E3108}')


class IScriptErrorList(IDispatch):
    """Script Error List Interface"""
    _iid_ = GUID('{F3470F24-15FD-11D2-BB2E-00805FF7EFCA}')


class _SearchAssistantEvents(dispinterface):
    _iid_ = GUID('{1611FDDA-445B-11D2-85DE-00C04FA35C89}')


class IShellFavoritesNameSpace(IDispatch):
    """IShellFavoritesNameSpace Interface"""
    _iid_ = GUID('{55136804-B2DE-11D1-B9F2-00A0C98BC547}')


IWebBrowser2._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "GoBack", )),
    (STDMETHOD(HRESULT, "GoForward", )),
    (STDMETHOD(HRESULT, "GoHome", )),
    (STDMETHOD(HRESULT, "GoSearch", )),
    (STDMETHOD(HRESULT, "Navigate", BSTR, POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "Refresh", )),
    (STDMETHOD(HRESULT, "Refresh2", POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "Stop", )),
    (STDMETHOD(HRESULT, "_get_Application", )),
    (STDMETHOD(HRESULT, "_get_Parent", )),
    (STDMETHOD(HRESULT, "_get_Container", )),
    (STDMETHOD(HRESULT, "_get_Document", )),
    (STDMETHOD(HRESULT, "_get_TopLevelContainer", )),
    (STDMETHOD(HRESULT, "_get_Type", )),
    (STDMETHOD(HRESULT, "_get_Left", )),
    (STDMETHOD(HRESULT, "_put_Left", c_long)),
    (STDMETHOD(HRESULT, "_get_Top", )),
    (STDMETHOD(HRESULT, "_put_Top", c_long)),
    (STDMETHOD(HRESULT, "_get_Width", )),
    (STDMETHOD(HRESULT, "_put_Width", c_long)),
    (STDMETHOD(HRESULT, "_get_Height", )),
    (STDMETHOD(HRESULT, "_put_Height", c_long)),
    (STDMETHOD(HRESULT, "_get_LocationName", )),
    (STDMETHOD(HRESULT, "_get_LocationURL", )),
    (STDMETHOD(HRESULT, "_get_Busy", )),
    (STDMETHOD(HRESULT, "Quit", )),
    (STDMETHOD(HRESULT, "ClientToWindow", POINTER(c_int), POINTER(c_int))),
    (STDMETHOD(HRESULT, "PutProperty", BSTR, VARIANT)),
    (STDMETHOD(HRESULT, "GetProperty", BSTR)),
    (STDMETHOD(HRESULT, "_get_Name", )),
    (STDMETHOD(HRESULT, "_get_HWND", )),
    (STDMETHOD(HRESULT, "_get_FullName", )),
    (STDMETHOD(HRESULT, "_get_Path", )),
    (STDMETHOD(HRESULT, "_get_Visible", )),
    (STDMETHOD(HRESULT, "_put_Visible", c_int)),
    (STDMETHOD(HRESULT, "_get_StatusBar", )),
    (STDMETHOD(HRESULT, "_put_StatusBar", c_int)),
    (STDMETHOD(HRESULT, "_get_StatusText", )),
    (STDMETHOD(HRESULT, "_put_StatusText", BSTR)),
    (STDMETHOD(HRESULT, "_get_ToolBar", )),
    (STDMETHOD(HRESULT, "_put_ToolBar", c_int)),
    (STDMETHOD(HRESULT, "_get_MenuBar", )),
    (STDMETHOD(HRESULT, "_put_MenuBar", c_int)),
    (STDMETHOD(HRESULT, "_get_FullScreen", )),
    (STDMETHOD(HRESULT, "_put_FullScreen", c_int)),
    (STDMETHOD(HRESULT, "Navigate2", POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "QueryStatusWB", OLECMDID)),
    (STDMETHOD(HRESULT, "ExecWB", OLECMDID, OLECMDEXECOPT, POINTER(VARIANT), POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "ShowBrowserBar", POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "_get_ReadyState", )),
    (STDMETHOD(HRESULT, "_get_Offline", )),
    (STDMETHOD(HRESULT, "_put_Offline", c_int)),
    (STDMETHOD(HRESULT, "_get_Silent", )),
    (STDMETHOD(HRESULT, "_put_Silent", c_int)),
    (STDMETHOD(HRESULT, "_get_RegisterAsBrowser", )),
    (STDMETHOD(HRESULT, "_put_RegisterAsBrowser", c_int)),
    (STDMETHOD(HRESULT, "_get_RegisterAsDropTarget", )),
    (STDMETHOD(HRESULT, "_put_RegisterAsDropTarget", c_int)),
    (STDMETHOD(HRESULT, "_get_TheaterMode", )),
    (STDMETHOD(HRESULT, "_put_TheaterMode", c_int)),
    (STDMETHOD(HRESULT, "_get_AddressBar", )),
    (STDMETHOD(HRESULT, "_put_AddressBar", c_int)),
    (STDMETHOD(HRESULT, "_get_Resizable", )),
    (STDMETHOD(HRESULT, "_put_Resizable", c_int)),
]

IShellWindows._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "_get_Count", )),
    (STDMETHOD(HRESULT, "Item", VARIANT)),
    (STDMETHOD(HRESULT, "_NewEnum", )),
    (STDMETHOD(HRESULT, "Register", POINTER(IDispatch), c_long, c_int, POINTER(c_long))),
    (STDMETHOD(HRESULT, "RegisterPending", c_long, POINTER(VARIANT), POINTER(VARIANT), c_int, POINTER(c_long))),
    (STDMETHOD(HRESULT, "Revoke", c_long)),
    (STDMETHOD(HRESULT, "OnNavigate", c_long, POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "OnActivated", c_long, c_int)),
    (STDMETHOD(HRESULT, "FindWindowSW", POINTER(VARIANT), POINTER(VARIANT), c_int, POINTER(c_long), c_int)),
    (STDMETHOD(HRESULT, "OnCreated", c_long, POINTER(IUnknown))),
    (STDMETHOD(HRESULT, "ProcessAttachDetach", c_int)),
]

IWebBrowser._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "GoBack", )),
    (STDMETHOD(HRESULT, "GoForward", )),
    (STDMETHOD(HRESULT, "GoHome", )),
    (STDMETHOD(HRESULT, "GoSearch", )),
    (STDMETHOD(HRESULT, "Navigate", BSTR, POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "Refresh", )),
    (STDMETHOD(HRESULT, "Refresh2", POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "Stop", )),
    (STDMETHOD(HRESULT, "_get_Application", )),
    (STDMETHOD(HRESULT, "_get_Parent", )),
    (STDMETHOD(HRESULT, "_get_Container", )),
    (STDMETHOD(HRESULT, "_get_Document", )),
    (STDMETHOD(HRESULT, "_get_TopLevelContainer", )),
    (STDMETHOD(HRESULT, "_get_Type", )),
    (STDMETHOD(HRESULT, "_get_Left", )),
    (STDMETHOD(HRESULT, "_put_Left", c_long)),
    (STDMETHOD(HRESULT, "_get_Top", )),
    (STDMETHOD(HRESULT, "_put_Top", c_long)),
    (STDMETHOD(HRESULT, "_get_Width", )),
    (STDMETHOD(HRESULT, "_put_Width", c_long)),
    (STDMETHOD(HRESULT, "_get_Height", )),
    (STDMETHOD(HRESULT, "_put_Height", c_long)),
    (STDMETHOD(HRESULT, "_get_LocationName", )),
    (STDMETHOD(HRESULT, "_get_LocationURL", )),
    (STDMETHOD(HRESULT, "_get_Busy", )),
]

ISearchAssistantOC._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "AddNextMenuItem", BSTR, c_long)),
    (STDMETHOD(HRESULT, "SetDefaultSearchUrl", BSTR)),
    (STDMETHOD(HRESULT, "NavigateToDefaultSearch", )),
    (STDMETHOD(HRESULT, "IsRestricted", BSTR)),
    (STDMETHOD(HRESULT, "_get_ShellFeaturesEnabled", )),
    (STDMETHOD(HRESULT, "_get_SearchAssistantDefault", )),
    (STDMETHOD(HRESULT, "_get_Searches", )),
    (STDMETHOD(HRESULT, "_get_InWebFolder", )),
    (STDMETHOD(HRESULT, "PutProperty", c_int, BSTR, BSTR)),
    (STDMETHOD(HRESULT, "GetProperty", c_int, BSTR)),
    (STDMETHOD(HRESULT, "_put_EventHandled", c_int)),
    (STDMETHOD(HRESULT, "ResetNextMenu", )),
    (STDMETHOD(HRESULT, "FindOnWeb", )),
    (STDMETHOD(HRESULT, "FindFilesOrFolders", )),
    (STDMETHOD(HRESULT, "FindComputer", )),
    (STDMETHOD(HRESULT, "FindPrinter", )),
    (STDMETHOD(HRESULT, "FindPeople", )),
    (STDMETHOD(HRESULT, "GetSearchAssistantURL", c_int, c_int)),
    (STDMETHOD(HRESULT, "NotifySearchSettingsChanged", )),
    (STDMETHOD(HRESULT, "_put_ASProvider", BSTR)),
    (STDMETHOD(HRESULT, "_get_ASProvider", )),
    (STDMETHOD(HRESULT, "_put_ASSetting", c_int)),
    (STDMETHOD(HRESULT, "_get_ASSetting", )),
    (STDMETHOD(HRESULT, "NETDetectNextNavigate", )),
    (STDMETHOD(HRESULT, "PutFindText", BSTR)),
    (STDMETHOD(HRESULT, "_get_Version", )),
    (STDMETHOD(HRESULT, "EncodeString", BSTR, BSTR, c_int)),
]

ISearches._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "_get_Count", )),
    (STDMETHOD(HRESULT, "_get_Default", )),
    (STDMETHOD(HRESULT, "Item", VARIANT)),
    (STDMETHOD(HRESULT, "_NewEnum", )),
]

DWebBrowserEvents._dispmethods_ = [
    (DISPMETHOD(0x64, None, "BeforeNavigate", BSTR, c_long, BSTR, POINTER(VARIANT), BSTR, POINTER(c_int))),
    (DISPMETHOD(0x65, None, "NavigateComplete", BSTR)),
    (DISPMETHOD(0x66, None, "StatusTextChange", BSTR)),
    (DISPMETHOD(0x6c, None, "ProgressChange", c_long, c_long)),
    (DISPMETHOD(0x68, None, "DownloadComplete", )),
    (DISPMETHOD(0x69, None, "CommandStateChange", c_long, c_int)),
    (DISPMETHOD(0x6a, None, "DownloadBegin", )),
    (DISPMETHOD(0x6b, None, "NewWindow", BSTR, c_long, BSTR, POINTER(VARIANT), BSTR, POINTER(c_int))),
    (DISPMETHOD(0x71, None, "TitleChange", BSTR)),
    (DISPMETHOD(0xc8, None, "FrameBeforeNavigate", BSTR, c_long, BSTR, POINTER(VARIANT), BSTR, POINTER(c_int))),
    (DISPMETHOD(0xc9, None, "FrameNavigateComplete", BSTR)),
    (DISPMETHOD(0xcc, None, "FrameNewWindow", BSTR, c_long, BSTR, POINTER(VARIANT), BSTR, POINTER(c_int))),
    (DISPMETHOD(0x67, None, "Quit", POINTER(c_int))),
    (DISPMETHOD(0x6d, None, "WindowMove", )),
    (DISPMETHOD(0x6e, None, "WindowResize", )),
    (DISPMETHOD(0x6f, None, "WindowActivate", )),
    (DISPMETHOD(0x70, None, "PropertyChange", BSTR)),
]

ISearchAssistantOC3._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "AddNextMenuItem", BSTR, c_long)),
    (STDMETHOD(HRESULT, "SetDefaultSearchUrl", BSTR)),
    (STDMETHOD(HRESULT, "NavigateToDefaultSearch", )),
    (STDMETHOD(HRESULT, "IsRestricted", BSTR)),
    (STDMETHOD(HRESULT, "_get_ShellFeaturesEnabled", )),
    (STDMETHOD(HRESULT, "_get_SearchAssistantDefault", )),
    (STDMETHOD(HRESULT, "_get_Searches", )),
    (STDMETHOD(HRESULT, "_get_InWebFolder", )),
    (STDMETHOD(HRESULT, "PutProperty", c_int, BSTR, BSTR)),
    (STDMETHOD(HRESULT, "GetProperty", c_int, BSTR)),
    (STDMETHOD(HRESULT, "_put_EventHandled", c_int)),
    (STDMETHOD(HRESULT, "ResetNextMenu", )),
    (STDMETHOD(HRESULT, "FindOnWeb", )),
    (STDMETHOD(HRESULT, "FindFilesOrFolders", )),
    (STDMETHOD(HRESULT, "FindComputer", )),
    (STDMETHOD(HRESULT, "FindPrinter", )),
    (STDMETHOD(HRESULT, "FindPeople", )),
    (STDMETHOD(HRESULT, "GetSearchAssistantURL", c_int, c_int)),
    (STDMETHOD(HRESULT, "NotifySearchSettingsChanged", )),
    (STDMETHOD(HRESULT, "_put_ASProvider", BSTR)),
    (STDMETHOD(HRESULT, "_get_ASProvider", )),
    (STDMETHOD(HRESULT, "_put_ASSetting", c_int)),
    (STDMETHOD(HRESULT, "_get_ASSetting", )),
    (STDMETHOD(HRESULT, "NETDetectNextNavigate", )),
    (STDMETHOD(HRESULT, "PutFindText", BSTR)),
    (STDMETHOD(HRESULT, "_get_Version", )),
    (STDMETHOD(HRESULT, "EncodeString", BSTR, BSTR, c_int)),
    (STDMETHOD(HRESULT, "_get_ShowFindPrinter", )),
    (STDMETHOD(HRESULT, "_get_SearchCompanionAvailable", )),
    (STDMETHOD(HRESULT, "_put_UseSearchCompanion", c_int)),
    (STDMETHOD(HRESULT, "_get_UseSearchCompanion", )),
]

IWebBrowserApp._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "GoBack", )),
    (STDMETHOD(HRESULT, "GoForward", )),
    (STDMETHOD(HRESULT, "GoHome", )),
    (STDMETHOD(HRESULT, "GoSearch", )),
    (STDMETHOD(HRESULT, "Navigate", BSTR, POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "Refresh", )),
    (STDMETHOD(HRESULT, "Refresh2", POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "Stop", )),
    (STDMETHOD(HRESULT, "_get_Application", )),
    (STDMETHOD(HRESULT, "_get_Parent", )),
    (STDMETHOD(HRESULT, "_get_Container", )),
    (STDMETHOD(HRESULT, "_get_Document", )),
    (STDMETHOD(HRESULT, "_get_TopLevelContainer", )),
    (STDMETHOD(HRESULT, "_get_Type", )),
    (STDMETHOD(HRESULT, "_get_Left", )),
    (STDMETHOD(HRESULT, "_put_Left", c_long)),
    (STDMETHOD(HRESULT, "_get_Top", )),
    (STDMETHOD(HRESULT, "_put_Top", c_long)),
    (STDMETHOD(HRESULT, "_get_Width", )),
    (STDMETHOD(HRESULT, "_put_Width", c_long)),
    (STDMETHOD(HRESULT, "_get_Height", )),
    (STDMETHOD(HRESULT, "_put_Height", c_long)),
    (STDMETHOD(HRESULT, "_get_LocationName", )),
    (STDMETHOD(HRESULT, "_get_LocationURL", )),
    (STDMETHOD(HRESULT, "_get_Busy", )),
    (STDMETHOD(HRESULT, "Quit", )),
    (STDMETHOD(HRESULT, "ClientToWindow", POINTER(c_int), POINTER(c_int))),
    (STDMETHOD(HRESULT, "PutProperty", BSTR, VARIANT)),
    (STDMETHOD(HRESULT, "GetProperty", BSTR)),
    (STDMETHOD(HRESULT, "_get_Name", )),
    (STDMETHOD(HRESULT, "_get_HWND", )),
    (STDMETHOD(HRESULT, "_get_FullName", )),
    (STDMETHOD(HRESULT, "_get_Path", )),
    (STDMETHOD(HRESULT, "_get_Visible", )),
    (STDMETHOD(HRESULT, "_put_Visible", c_int)),
    (STDMETHOD(HRESULT, "_get_StatusBar", )),
    (STDMETHOD(HRESULT, "_put_StatusBar", c_int)),
    (STDMETHOD(HRESULT, "_get_StatusText", )),
    (STDMETHOD(HRESULT, "_put_StatusText", BSTR)),
    (STDMETHOD(HRESULT, "_get_ToolBar", )),
    (STDMETHOD(HRESULT, "_put_ToolBar", c_int)),
    (STDMETHOD(HRESULT, "_get_MenuBar", )),
    (STDMETHOD(HRESULT, "_put_MenuBar", c_int)),
    (STDMETHOD(HRESULT, "_get_FullScreen", )),
    (STDMETHOD(HRESULT, "_put_FullScreen", c_int)),
]

DWebBrowserEvents2._dispmethods_ = [
    (DISPMETHOD(0x66, None, "StatusTextChange", BSTR)),
    (DISPMETHOD(0x6c, None, "ProgressChange", c_long, c_long)),
    (DISPMETHOD(0x69, None, "CommandStateChange", c_long, c_int)),
    (DISPMETHOD(0x6a, None, "DownloadBegin", )),
    (DISPMETHOD(0x68, None, "DownloadComplete", )),
    (DISPMETHOD(0x71, None, "TitleChange", BSTR)),
    (DISPMETHOD(0x70, None, "PropertyChange", BSTR)),
    (DISPMETHOD(0xfa, None, "BeforeNavigate2", POINTER(IDispatch), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(c_int))),
    (DISPMETHOD(0xfb, None, "NewWindow2", POINTER(POINTER(IDispatch)), POINTER(c_int))),
    (DISPMETHOD(0xfc, None, "NavigateComplete2", POINTER(IDispatch), POINTER(VARIANT))),
    (DISPMETHOD(0x103, None, "DocumentComplete", POINTER(IDispatch), POINTER(VARIANT))),
    (DISPMETHOD(0xfd, None, "OnQuit", )),
    (DISPMETHOD(0xfe, None, "OnVisible", c_int)),
    (DISPMETHOD(0xff, None, "OnToolBar", c_int)),
    (DISPMETHOD(0x100, None, "OnMenuBar", c_int)),
    (DISPMETHOD(0x101, None, "OnStatusBar", c_int)),
    (DISPMETHOD(0x102, None, "OnFullScreen", c_int)),
    (DISPMETHOD(0x104, None, "OnTheaterMode", c_int)),
    (DISPMETHOD(0x106, None, "WindowSetResizable", c_int)),
    (DISPMETHOD(0x108, None, "WindowSetLeft", c_long)),
    (DISPMETHOD(0x109, None, "WindowSetTop", c_long)),
    (DISPMETHOD(0x10a, None, "WindowSetWidth", c_long)),
    (DISPMETHOD(0x10b, None, "WindowSetHeight", c_long)),
    (DISPMETHOD(0x107, None, "WindowClosing", c_int, POINTER(c_int))),
    (DISPMETHOD(0x10c, None, "ClientToHostWindow", POINTER(c_long), POINTER(c_long))),
    (DISPMETHOD(0x10d, None, "SetSecureLockIcon", c_long)),
    (DISPMETHOD(0x10e, None, "FileDownload", POINTER(c_int))),
    (DISPMETHOD(0x10f, None, "NavigateError", POINTER(IDispatch), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(c_int))),
    (DISPMETHOD(0xe1, None, "PrintTemplateInstantiation", POINTER(IDispatch))),
    (DISPMETHOD(0xe2, None, "PrintTemplateTeardown", POINTER(IDispatch))),
    (DISPMETHOD(0xe3, None, "UpdatePageStatus", POINTER(IDispatch), POINTER(VARIANT), POINTER(VARIANT))),
    (DISPMETHOD(0x110, None, "PrivacyImpactedStateChange", c_int)),
]

DShellWindowsEvents._dispmethods_ = [
    (DISPMETHOD(0xc8, None, "WindowRegistered", c_long)),
    (DISPMETHOD(0xc9, None, "WindowRevoked", c_long)),
]

ISearchAssistantOC2._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "AddNextMenuItem", BSTR, c_long)),
    (STDMETHOD(HRESULT, "SetDefaultSearchUrl", BSTR)),
    (STDMETHOD(HRESULT, "NavigateToDefaultSearch", )),
    (STDMETHOD(HRESULT, "IsRestricted", BSTR)),
    (STDMETHOD(HRESULT, "_get_ShellFeaturesEnabled", )),
    (STDMETHOD(HRESULT, "_get_SearchAssistantDefault", )),
    (STDMETHOD(HRESULT, "_get_Searches", )),
    (STDMETHOD(HRESULT, "_get_InWebFolder", )),
    (STDMETHOD(HRESULT, "PutProperty", c_int, BSTR, BSTR)),
    (STDMETHOD(HRESULT, "GetProperty", c_int, BSTR)),
    (STDMETHOD(HRESULT, "_put_EventHandled", c_int)),
    (STDMETHOD(HRESULT, "ResetNextMenu", )),
    (STDMETHOD(HRESULT, "FindOnWeb", )),
    (STDMETHOD(HRESULT, "FindFilesOrFolders", )),
    (STDMETHOD(HRESULT, "FindComputer", )),
    (STDMETHOD(HRESULT, "FindPrinter", )),
    (STDMETHOD(HRESULT, "FindPeople", )),
    (STDMETHOD(HRESULT, "GetSearchAssistantURL", c_int, c_int)),
    (STDMETHOD(HRESULT, "NotifySearchSettingsChanged", )),
    (STDMETHOD(HRESULT, "_put_ASProvider", BSTR)),
    (STDMETHOD(HRESULT, "_get_ASProvider", )),
    (STDMETHOD(HRESULT, "_put_ASSetting", c_int)),
    (STDMETHOD(HRESULT, "_get_ASSetting", )),
    (STDMETHOD(HRESULT, "NETDetectNextNavigate", )),
    (STDMETHOD(HRESULT, "PutFindText", BSTR)),
    (STDMETHOD(HRESULT, "_get_Version", )),
    (STDMETHOD(HRESULT, "EncodeString", BSTR, BSTR, c_int)),
    (STDMETHOD(HRESULT, "_get_ShowFindPrinter", )),
]

ISearch._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "_get_Title", )),
    (STDMETHOD(HRESULT, "_get_Id", )),
    (STDMETHOD(HRESULT, "_get_URL", )),
]

IShellUIHelper._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "ResetFirstBootMode", )),
    (STDMETHOD(HRESULT, "ResetSafeMode", )),
    (STDMETHOD(HRESULT, "RefreshOfflineDesktop", )),
    (STDMETHOD(HRESULT, "AddFavorite", BSTR, POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "AddChannel", BSTR)),
    (STDMETHOD(HRESULT, "AddDesktopComponent", BSTR, BSTR, POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT), POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "IsSubscribed", BSTR)),
    (STDMETHOD(HRESULT, "NavigateAndFind", BSTR, BSTR, POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "ImportExportFavorites", c_int, BSTR)),
    (STDMETHOD(HRESULT, "AutoCompleteSaveForm", POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "AutoScan", BSTR, BSTR, POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "AutoCompleteAttach", POINTER(VARIANT))),
    (STDMETHOD(HRESULT, "ShowBrowserUI", BSTR, POINTER(VARIANT))),
]

DShellNameSpaceEvents._dispmethods_ = [
    (DISPMETHOD(0x1, None, "FavoritesSelectionChange", c_long, c_long, BSTR, BSTR, c_long, BSTR, c_long)),
    (DISPMETHOD(0x2, None, "SelectionChange", )),
    (DISPMETHOD(0x3, None, "DoubleClick", )),
    (DISPMETHOD(0x4, None, "Initialized", )),
]

IShellNameSpace._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "MoveSelectionUp", )),
    (STDMETHOD(HRESULT, "MoveSelectionDown", )),
    (STDMETHOD(HRESULT, "ResetSort", )),
    (STDMETHOD(HRESULT, "NewFolder", )),
    (STDMETHOD(HRESULT, "Synchronize", )),
    (STDMETHOD(HRESULT, "Import", )),
    (STDMETHOD(HRESULT, "Export", )),
    (STDMETHOD(HRESULT, "InvokeContextMenuCommand", BSTR)),
    (STDMETHOD(HRESULT, "MoveSelectionTo", )),
    (STDMETHOD(HRESULT, "_get_SubscriptionsEnabled", )),
    (STDMETHOD(HRESULT, "CreateSubscriptionForSelection", )),
    (STDMETHOD(HRESULT, "DeleteSubscriptionForSelection", )),
    (STDMETHOD(HRESULT, "SetRoot", BSTR)),
    (STDMETHOD(HRESULT, "_get_EnumOptions", )),
    (STDMETHOD(HRESULT, "_put_EnumOptions", c_long)),
    (STDMETHOD(HRESULT, "_get_SelectedItem", )),
    (STDMETHOD(HRESULT, "_put_SelectedItem", POINTER(IDispatch))),
    (STDMETHOD(HRESULT, "_get_Root", )),
    (STDMETHOD(HRESULT, "_put_Root", VARIANT)),
    (STDMETHOD(HRESULT, "_get_Depth", )),
    (STDMETHOD(HRESULT, "_put_Depth", c_int)),
    (STDMETHOD(HRESULT, "_get_Mode", )),
    (STDMETHOD(HRESULT, "_put_Mode", c_uint)),
    (STDMETHOD(HRESULT, "_get_Flags", )),
    (STDMETHOD(HRESULT, "_put_Flags", c_ulong)),
    (STDMETHOD(HRESULT, "_put_TVFlags", c_ulong)),
    (STDMETHOD(HRESULT, "_get_TVFlags", )),
    (STDMETHOD(HRESULT, "_get_Columns", )),
    (STDMETHOD(HRESULT, "_put_Columns", BSTR)),
    (STDMETHOD(HRESULT, "_get_CountViewTypes", )),
    (STDMETHOD(HRESULT, "SetViewType", c_int)),
    (STDMETHOD(HRESULT, "SelectedItems", )),
    (STDMETHOD(HRESULT, "Expand", VARIANT, c_int)),
    (STDMETHOD(HRESULT, "UnselectAll", )),
]

IScriptErrorList._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "advanceError", )),
    (STDMETHOD(HRESULT, "retreatError", )),
    (STDMETHOD(HRESULT, "canAdvanceError", )),
    (STDMETHOD(HRESULT, "canRetreatError", )),
    (STDMETHOD(HRESULT, "getErrorLine", )),
    (STDMETHOD(HRESULT, "getErrorChar", )),
    (STDMETHOD(HRESULT, "getErrorCode", )),
    (STDMETHOD(HRESULT, "getErrorMsg", )),
    (STDMETHOD(HRESULT, "getErrorUrl", )),
    (STDMETHOD(HRESULT, "getAlwaysShowLockState", )),
    (STDMETHOD(HRESULT, "getDetailsPaneOpen", )),
    (STDMETHOD(HRESULT, "setDetailsPaneOpen", c_long)),
    (STDMETHOD(HRESULT, "getPerErrorDisplay", )),
    (STDMETHOD(HRESULT, "setPerErrorDisplay", c_long)),
]

_SearchAssistantEvents._dispmethods_ = [
    (DISPMETHOD(0x1, None, "OnNextMenuSelect", c_long)),
    (DISPMETHOD(0x2, None, "OnNewSearch", )),
]

IShellFavoritesNameSpace._methods_ = IDispatch._methods_ + [
    (STDMETHOD(HRESULT, "MoveSelectionUp", )),
    (STDMETHOD(HRESULT, "MoveSelectionDown", )),
    (STDMETHOD(HRESULT, "ResetSort", )),
    (STDMETHOD(HRESULT, "NewFolder", )),
    (STDMETHOD(HRESULT, "Synchronize", )),
    (STDMETHOD(HRESULT, "Import", )),
    (STDMETHOD(HRESULT, "Export", )),
    (STDMETHOD(HRESULT, "InvokeContextMenuCommand", BSTR)),
    (STDMETHOD(HRESULT, "MoveSelectionTo", )),
    (STDMETHOD(HRESULT, "_get_SubscriptionsEnabled", )),
    (STDMETHOD(HRESULT, "CreateSubscriptionForSelection", )),
    (STDMETHOD(HRESULT, "DeleteSubscriptionForSelection", )),
    (STDMETHOD(HRESULT, "SetRoot", BSTR)),
]

##############################################################################

class ShellWindows(COMObject):
    """ShellDispatch Load in Shell Context"""
    _regclsid_ = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'
    _com_interfaces_ = [IShellWindows]
    _outgoing_interfaces_ = [DShellWindowsEvents]


class ShellNameSpace(COMObject):
    _regclsid_ = '{55136805-B2DE-11D1-B9F2-00A0C98BC547}'
    _com_interfaces_ = [IShellNameSpace]
    _outgoing_interfaces_ = [DShellNameSpaceEvents]


class CScriptErrorList(COMObject):
    _regclsid_ = '{EFD01300-160F-11D2-BB2E-00805FF7EFCA}'
    _com_interfaces_ = [IScriptErrorList]


class InternetExplorer(COMObject):
    """Internet Explorer Application."""
    _regclsid_ = '{0002DF01-0000-0000-C000-000000000046}'
    _com_interfaces_ = [IWebBrowser2, IWebBrowserApp]
    _outgoing_interfaces_ = [DWebBrowserEvents2, DWebBrowserEvents]


class ShellBrowserWindow(COMObject):
    """Shell Browser Window."""
    _regclsid_ = '{C08AFD90-F2A1-11D1-8455-00A0C91F3880}'
    _com_interfaces_ = [IWebBrowser2, IWebBrowserApp]
    _outgoing_interfaces_ = [DWebBrowserEvents2, DWebBrowserEvents]


class WebBrowser_V1(COMObject):
    """WebBrowser Control"""
    _regclsid_ = '{EAB22AC3-30C1-11CF-A7EB-0000C05BAE0B}'
    _com_interfaces_ = [IWebBrowser, IWebBrowser2]
    _outgoing_interfaces_ = [DWebBrowserEvents, DWebBrowserEvents2]


class WebBrowser(COMObject):
    """WebBrowser Control"""
    _regclsid_ = '{8856F961-340A-11D0-A96B-00C04FD705A2}'
    _com_interfaces_ = [IWebBrowser2, IWebBrowser]
    _outgoing_interfaces_ = [DWebBrowserEvents2, DWebBrowserEvents]


class ShellUIHelper(COMObject):
    _regclsid_ = '{64AB4BB7-111E-11D1-8F79-00C04FC2FBE1}'
    _com_interfaces_ = [IShellUIHelper]


class SearchAssistantOC(COMObject):
    """SearchAssistantOC Class"""
    _regclsid_ = '{B45FF030-4447-11D2-85DE-00C04FA35C89}'
    _com_interfaces_ = [ISearchAssistantOC3]
    _outgoing_interfaces_ = [_SearchAssistantEvents]

