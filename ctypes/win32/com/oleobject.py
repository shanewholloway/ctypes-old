from ctypes import *
from ctypes.wintypes import BYTE, WORD, DWORD, MSG, HWND, RECT
from ctypes.com import IUnknown, STDMETHOD, HRESULT, GUID, ole32
from ctypes.com.ole import IAdviseSink, SIZEL, LOGPALETTE

# fake
IMoniker = IUnknown
IDataObject = IUnknown
IEnumOleVerb = IUnknown
IOleContainer = IUnknown

IEnumSTATDATA = IUnknown

LPCOLESTR = c_wchar_p
LPOLESTR = c_wchar_p
BOOL = c_int
LONG = c_long
LPMSG = POINTER(MSG)
LPRECT = POINTER(RECT)

class IOleClientSite(IUnknown):
    _iid_ = GUID("{00000118-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "SaveObject"),
        STDMETHOD(HRESULT, "GetMoniker", DWORD, DWORD, POINTER(POINTER(IMoniker))),
        STDMETHOD(HRESULT, "GetContainer", POINTER(POINTER(IOleContainer))),
        STDMETHOD(HRESULT, "ShowObject"),
        STDMETHOD(HRESULT, "OnShowWindow", BOOL),
        STDMETHOD(HRESULT, "RequestNewObjectLayout")]

class IOleObject(IUnknown):
    _iid_ = GUID("{00000112-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "SetClientSite", POINTER(IOleClientSite)),
        STDMETHOD(HRESULT, "GetClientSite", POINTER(POINTER(IOleClientSite))),
        STDMETHOD(HRESULT, "SetHostNames", LPCOLESTR, LPCOLESTR),
        STDMETHOD(HRESULT, "Close", DWORD),
        STDMETHOD(HRESULT, "SetMoniker", DWORD, POINTER(IMoniker)),
        STDMETHOD(HRESULT, "GetMoniker", DWORD, DWORD, POINTER(POINTER(IMoniker))),
        STDMETHOD(HRESULT, "InitFromData", POINTER(IDataObject), BOOL, DWORD),
        STDMETHOD(HRESULT, "GetClipboardData", DWORD, POINTER(POINTER(IDataObject))),
        STDMETHOD(HRESULT, "DoVerb", LONG, LPMSG, POINTER(IOleClientSite), LONG, HWND, LPRECT),
        STDMETHOD(HRESULT, "EnumVerbs", POINTER(POINTER(IEnumOleVerb))),
        STDMETHOD(HRESULT, "Update"),
        STDMETHOD(HRESULT, "IsUpToDate"),
        STDMETHOD(HRESULT, "GetUserClassID", POINTER(GUID)),
        STDMETHOD(HRESULT, "GetUserType", DWORD, POINTER(LPOLESTR)),
        STDMETHOD(HRESULT, "SetExtent", DWORD, POINTER(SIZEL)),
        STDMETHOD(HRESULT, "GetExtent", DWORD, POINTER(SIZEL)),
        STDMETHOD(HRESULT, "Advise", POINTER(IAdviseSink), POINTER(DWORD)),
        STDMETHOD(HRESULT, "Unadvise", DWORD),
        STDMETHOD(HRESULT, "EnumAdvise", POINTER(POINTER(IEnumSTATDATA))),
        STDMETHOD(HRESULT, "GetMiscStatus", DWORD, POINTER(DWORD)),
        STDMETHOD(HRESULT, "SetColorScheme", POINTER(LOGPALETTE))]

class IOleAdviseHolder(IUnknown):
    _iid_ = GUID("{00000111-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "Advise", POINTER(IAdviseSink), POINTER(DWORD)),
        STDMETHOD(HRESULT, "Unadvise", DWORD),
        STDMETHOD(HRESULT, "EnumAdvise", POINTER(POINTER(IEnumSTATDATA))),
        STDMETHOD(HRESULT, "SendOnRename", POINTER(IMoniker)),
        STDMETHOD(HRESULT, "SendOnSave"),
        STDMETHOD(HRESULT, "SendOnClose")]

def CreateOleAdviseHolder():
    p = POINTER(IOleAdviseHolder)()
    ole32.CreateOleAdviseHolder(byref(p))
    return p

if __name__ == "__main__":
    holder = CreateOleAdviseHolder()
    print holder
    holder.SendOnSave()
    holder.SendOnClose()
