from ctypes import *
from ctypes.com import IUnknown, GUID, HRESULT, STDMETHOD
from ctypes.wintypes import DWORD


LPCOLESTR = c_wchar_p
BOOL = c_int

class IPersist(IUnknown):
    _iid_ = GUID("{0000010C-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "GetClassID", POINTER(GUID))
        ]


# needs IStream
##class IPersistStream(IPersist):
##    _iid_ = GUID("{00000109-0000-0000-C000-000000000046}")
##    _methods_ = IPersist._methods_ + [
##        STDMETHOD(HRESULT, "IsDirty"),
##        STDMETHOD(HRESULT, "Load", POINTER(IStream)),
##        STDMETHOD(HRESULT, "Save", POINTER(IStream), BOOL),
##        STDMETHOD(HRESULT, "GetSizeMax", POINTER(c_longlong))
##        ]

class IPersistFile(IPersist):
    _iid_ = GUID("{0000010B-0000-0000-C000-000000000046}")
    _methods_ = IPersist._methods_ + [
        STDMETHOD(HRESULT, "IsDirty"),
        STDMETHOD(HRESULT, "Load", LPCOLESTR, DWORD),
        STDMETHOD(HRESULT, "Save", LPCOLESTR, BOOL),
        STDMETHOD(HRESULT, "SaveCompleted", LPCOLESTR),
        # Returned string pointer must be freed with IMalloc::Free
        # How would we do this?
        STDMETHOD(HRESULT, "GetCurFile", POINTER(LPCOLESTR))
        ]

__all__ = ["Persist", "IPersistFile"]
