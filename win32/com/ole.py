from ctcom import IUnknown, STDMETHOD, HRESULT, GUID, COMPointer

from ctypes import c_int, POINTER, Structure
from windows import MSG, RECT, OLESTR

BORDERWIDTHS = RECT

class IOleWindow(IUnknown):
    _iid_ = GUID("{00000114-0000-0000-C000-000000000046}")

class IOleWindowPointer(COMPointer):
    _interface_ = IOleWindow


class IOleInPlaceUIWindow(IOleWindow):
    _iid_ = GUID("{00000115-0000-0000-C000-000000000046}")

class IOleInPlaceUIWindowPointer(COMPointer):
    _interface_ = IOleInPlaceUIWindow


class IOleInPlaceActiveObject(IOleWindow):
    _iid_ = GUID("{00000117-0000-0000-C000-000000000046}")

class IOleInPlaceActiveObjectPointer(COMPointer):
    _interface_ = IOleInPlaceActiveObject


IOleWindow._methods_ = [
    STDMETHOD(HRESULT, "GetWindow", POINTER(c_int)),
    STDMETHOD(HRESULT, "ContextSensitiveHelp", c_int)]

IOleInPlaceUIWindow._methods_ = [
    STDMETHOD(HRESULT, "GetBorder", POINTER(RECT)),
    STDMETHOD(HRESULT, "RequestBorderSpace", POINTER(BORDERWIDTHS)),
    STDMETHOD(HRESULT, "SetBorderSpace", POINTER(BORDERWIDTHS)),
    STDMETHOD(HRESULT, "SetActiveObject", IOleInPlaceActiveObjectPointer, POINTER(OLESTR))]

IOleInPlaceActiveObject._methods_ = [
    STDMETHOD(HRESULT, "TranslateAccelerator", POINTER(MSG)),
    STDMETHOD(HRESULT, "OnFrameWindowActivate", c_int),
    STDMETHOD(HRESULT, "OnDocWindowActivate", c_int),
    STDMETHOD(HRESULT, "ResizeBorder", POINTER(RECT), IOleInPlaceUIWindowPointer, c_int),
    STDMETHOD(HRESULT, "EnableModeless", c_int)]
