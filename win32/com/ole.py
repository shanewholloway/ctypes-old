from ctypes import *
from ctypes.wintypes import DWORD, MSG, SIZEL, RECTL, RECT, OLESTR, HDC
from ctypes.com import IUnknown, STDMETHOD, HRESULT, GUID

BORDERWIDTHS = RECT

class IOleWindow(IUnknown):
    _iid_ = GUID("{00000114-0000-0000-C000-000000000046}")

class IOleInPlaceUIWindow(IOleWindow):
    _iid_ = GUID("{00000115-0000-0000-C000-000000000046}")

class IOleInPlaceActiveObject(IOleWindow):
    _iid_ = GUID("{00000117-0000-0000-C000-000000000046}")

IOleWindow._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "GetWindow", POINTER(c_int)),
    STDMETHOD(HRESULT, "ContextSensitiveHelp", c_int)]

IOleInPlaceUIWindow._methods_ = IOleWindow._methods_ + [
    STDMETHOD(HRESULT, "GetBorder", POINTER(RECT)),
    STDMETHOD(HRESULT, "RequestBorderSpace", POINTER(BORDERWIDTHS)),
    STDMETHOD(HRESULT, "SetBorderSpace", POINTER(BORDERWIDTHS)),
    STDMETHOD(HRESULT, "SetActiveObject", POINTER(IOleInPlaceActiveObject), POINTER(OLESTR))]

IOleInPlaceActiveObject._methods_ = IOleWindow._methods_ + [
    STDMETHOD(HRESULT, "TranslateAccelerator", POINTER(MSG)),
    STDMETHOD(HRESULT, "OnFrameWindowActivate", c_int),
    STDMETHOD(HRESULT, "OnDocWindowActivate", c_int),
    STDMETHOD(HRESULT, "ResizeBorder", POINTER(RECT), POINTER(IOleInPlaceUIWindow), c_int),
    STDMETHOD(HRESULT, "EnableModeless", c_int)]


# Fakes:
void = c_int # Can we use None instead? Seems so, but not yet tested...
FORMATETC = c_int
STGMEDIUM = c_int
IMoniker = c_int
DVTARGETDEVICE = c_int
LOGPALETTE = c_int

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

################################################################


##__all__ = ["IOleWindow", "IOleInPlaceUIWindow", "IOleInPlaceActiveObject"]
