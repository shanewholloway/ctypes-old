from ctypes import *
from ctypes.com import IUnknown, GUID, HRESULT, STDMETHOD
from ctypes.wintypes import DWORD
from ctypes.com.automation import VARIANT
from ctypes.com.storage import IStream

LPCOLESTR = c_wchar_p
BOOL = c_int

class IPersist(IUnknown):
    _iid_ = GUID("{0000010C-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "GetClassID", POINTER(GUID))
        ]


class IPersistStream(IPersist):
    _iid_ = GUID("{00000109-0000-0000-C000-000000000046}")
    _methods_ = IPersist._methods_ + [
        STDMETHOD(HRESULT, "IsDirty"),
        STDMETHOD(HRESULT, "Load", POINTER(IStream)),
        STDMETHOD(HRESULT, "Save", POINTER(IStream), BOOL),
        STDMETHOD(HRESULT, "GetSizeMax", POINTER(c_longlong))
        ]

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

# fake:
IErrorLog = IUnknown
IPropertyBag = IUnknown

class IPropertyBag(IUnknown):
    _iid_ = GUID("{55272A00-42CB-11CE-8135-00AA004BB851}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "Read", LPCOLESTR, POINTER(VARIANT), POINTER(IErrorLog)),
        STDMETHOD(HRESULT, "Write", LPCOLESTR, POINTER(VARIANT))
        ]

class IPersistPropertyBag(IPersist):
    _iid_ = GUID("{37D84F60-42CB-11CE-8135-00AA004BB851}")
    _methods_ = IPersist._methods_ + [
        STDMETHOD(HRESULT, "InitNew"),
        STDMETHOD(HRESULT, "Load", POINTER(IPropertyBag), POINTER(IErrorLog)),
        STDMETHOD(HRESULT, "Save", POINTER(IPropertyBag), BOOL, BOOL)
        ]

__all__ = ["Persist", "IPersistFile", "IPropertyBag", "IPersistPropertyBag"]
