from ctypes import *
from ctypes.com import IUnknown, STDMETHOD, HRESULT, GUID
from ctypes.com.storage import IStream, IStorage
from ctypes.wintypes import BYTE, WORD, DWORD, MSG, SIZE, SIZEL, RECTL, RECT, LPOLESTR, HANDLE, \
     LPWSTR, BOOL, HWND, HMENU, HDC

CLIPFORMAT = WORD

HBITMAP = HANDLE
HOLEMENU = HGLOBAL = HENHMETAFILE = HMETAFILEPICT = HANDLE

# Fakes:
void = c_int # Can we use None instead? Seems so, but not yet tested...
IMoniker = IUnknown

class DVTARGETDEVICE(Structure):
    _fields_ = [("tdSize", DWORD),
                ("tdDriverNameOffset", WORD),
                ("tdDeviceNameOffset", WORD),
                ("tdPortNameOffset", WORD),
                ("tdExtDevmodeOffset", WORD),
                ("tdData", BYTE * 1)]

class FORMATETC(Structure):
    _fields_ = [("cfFormat", CLIPFORMAT),
                ("ptd", POINTER(DVTARGETDEVICE)),
                ("dwAspect", DWORD),
                ("lindex", c_long),
                ("tymed", DWORD)]
assert sizeof(FORMATETC) == 20

TYMED_NULL      = 0
TYMED_HGLOBAL   = 1
TYMED_FILE      = 2
TYMED_ISTREAM   = 4
TYMED_ISTORAGE  = 8
TYMED_GDI       = 16
TYMED_MFPICT    = 32
TYMED_ENHMF     = 64

class STGMEDIUM(Structure):
    class _u(Union):
        _fields_ = [("hBitmap", HBITMAP),
                    ("hMetaFilePict", HMETAFILEPICT),
                    ("hEnhMetaFile", HENHMETAFILE),
                    ("hGlobal", HGLOBAL),
                    ("lpszFileName", LPWSTR),
                    ("pstm", POINTER(IStream)),
                    ("pstg", POINTER(IStorage))]
    _fields_ = [("tymed", DWORD),
                ("_", _u),
                ("pUnkForRelease", POINTER(IUnknown))]

class PALETTEENTRY(Structure):
    _fields_ = [("peRed", BYTE),
                ("peGreen", BYTE),
                ("peBlue", BYTE),
                ("peFlags", BYTE)]

class LOGPALETTE(Structure):
    _fields_ = [("palVersion", WORD),
                ("palNumEntried", WORD),
                ("palPalEntry", PALETTEENTRY * 1)]


BORDERWIDTHS = RECT

class OLEINPLACEFRAMEINFO(Structure):
    _fields_ = [("cb", c_uint),
                ("fMDIApp", BOOL),
                ("hwndFrame", HWND),
                ("cAccelEntries", c_uint)]

class IOleWindow(IUnknown):
    _iid_ = GUID("{00000114-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "GetWindow", POINTER(HWND)),
        STDMETHOD(HRESULT, "ContextSensitiveHelp", c_int)]

class IOleInPlaceUIWindow(IOleWindow):
    _iid_ = GUID("{00000115-0000-0000-C000-000000000046}")

class IOleInPlaceActiveObject(IOleWindow):
    _iid_ = GUID("{00000117-0000-0000-C000-000000000046}")

IOleInPlaceUIWindow._methods_ = IOleWindow._methods_ + [
    STDMETHOD(HRESULT, "GetBorder", POINTER(RECT)),
    STDMETHOD(HRESULT, "RequestBorderSpace", POINTER(BORDERWIDTHS)),
    STDMETHOD(HRESULT, "SetBorderSpace", POINTER(BORDERWIDTHS)),
    STDMETHOD(HRESULT, "SetActiveObject", POINTER(IOleInPlaceActiveObject), LPOLESTR)]

IOleInPlaceActiveObject._methods_ = IOleWindow._methods_ + [
    STDMETHOD(HRESULT, "TranslateAccelerator", POINTER(MSG)),
    STDMETHOD(HRESULT, "OnFrameWindowActivate", c_int),
    STDMETHOD(HRESULT, "OnDocWindowActivate", c_int),
    STDMETHOD(HRESULT, "ResizeBorder", POINTER(RECT), POINTER(IOleInPlaceUIWindow), c_int),
    STDMETHOD(HRESULT, "EnableModeless", c_int)]

class OLEMENUGROUPWIDTHS(Structure):
    _fields_ = [("widths", c_long * 6)]

# functions: OleCreateMenuDescriptor, OleDestroyMenuDescriptor

class IOleInPlaceFrame(IOleInPlaceUIWindow):
    _iid_ = GUID("{00000116-0000-0000-C000-000000000046}")
    _methods_ = IOleInPlaceUIWindow._methods_ + [
        STDMETHOD(HRESULT, "InsertMenus", HMENU, POINTER(OLEMENUGROUPWIDTHS)),
        STDMETHOD(HRESULT, "SetMenu", HMENU, HOLEMENU, HWND),
        STDMETHOD(HRESULT, "RemoveMenus", HMENU),
        STDMETHOD(HRESULT, "SetStatusText", LPOLESTR),
        STDMETHOD(HRESULT, "EnableModeless", BOOL),
        STDMETHOD(HRESULT, "TranslateAccelerator", POINTER(MSG), WORD),
        ]

class IOleInPlaceObject(IOleWindow):
    _iid_ = GUID("{00000113-0000-0000-C000-000000000046}")
    _methods_ = IOleWindow._methods_ + [
        STDMETHOD(HRESULT, "InPlaceDeactivate"),
        STDMETHOD(HRESULT, "UIDeactivate"),
        STDMETHOD(HRESULT, "SetObjectRects", POINTER(RECT), POINTER(RECT)),
        STDMETHOD(HRESULT, "ReactivateAndUndo"),
        ]

class IOleInPlaceSite(IOleWindow):
    _iid_ = GUID("{00000119-0000-0000-C000-000000000046}")
    _methods_ = IOleWindow._methods_ + [
        STDMETHOD(HRESULT, "CanInPlaceActivate"),
        STDMETHOD(HRESULT, "OnInPlaceActivate"),
        STDMETHOD(HRESULT, "OnUIActivate"),
        STDMETHOD(HRESULT, "GetWindowContext",
                  POINTER(POINTER(IOleInPlaceFrame)),
                  POINTER(POINTER(IOleInPlaceUIWindow)),
                  POINTER(RECT), POINTER(RECT),
                  POINTER(OLEINPLACEFRAMEINFO)),
        STDMETHOD(HRESULT, "Scroll", SIZE),
        STDMETHOD(HRESULT, "OnUIDeactivate", BOOL),
        STDMETHOD(HRESULT, "OnInPlaceDeactivate"),
        STDMETHOD(HRESULT, "DiscardUndoState"),
        STDMETHOD(HRESULT, "DeactivateAndUndo"),
        STDMETHOD(HRESULT, "OnPosRectChange", POINTER(RECT))]

class IAdviseSink(IUnknown):
    _iid_ = GUID("{0000010F-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(void, "OnDataChange", POINTER(FORMATETC), POINTER(STGMEDIUM)),
        STDMETHOD(void, "OnViewChange", DWORD, c_long),
        STDMETHOD(void, "OnRename", POINTER(IMoniker)),
        STDMETHOD(void, "OnSave"),
        STDMETHOD(void, "OnClose")]

class IViewObject(IUnknown):
    _iid_ = GUID("{0000010D-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "Draw", DWORD, c_long, c_void_p,
                  POINTER(DVTARGETDEVICE), HDC, HDC, POINTER(RECTL),
                  POINTER(RECTL), c_void_p, DWORD),
        STDMETHOD(HRESULT, "GetColorSet", DWORD, c_long, c_void_p,
                  POINTER(DVTARGETDEVICE), HDC, POINTER(POINTER(LOGPALETTE))),
        STDMETHOD(HRESULT, "Freeze", DWORD, c_long, c_void_p, POINTER(DWORD)),
        STDMETHOD(HRESULT, "Unfreeze", DWORD),
        STDMETHOD(HRESULT, "SetAdvise", DWORD, DWORD, POINTER(IAdviseSink)),
        STDMETHOD(HRESULT, "GetAdvise", POINTER(DWORD), POINTER(DWORD),
                  POINTER(POINTER(IAdviseSink)))]

class IViewObject2(IViewObject):
    _iid_ = GUID("{00000127-0000-0000-C000-000000000046}")
    _methods_ = IViewObject._methods_ + [
        STDMETHOD(HRESULT, "GetExtent", DWORD, c_long,
                  POINTER(DVTARGETDEVICE), POINTER(SIZEL))]
