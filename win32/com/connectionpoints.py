# connect.py - ConnectionPoint support
from ctypes import POINTER, c_ulong, Structure, c_voidp
from ctypes.com import IUnknown, GUID, REFIID, STDMETHOD, HRESULT

################

DWORD = c_ulong

################

class CONNECTDATA(Structure):
    _fields_ = [("pUnk", POINTER(IUnknown)),
                ("dwCookie", DWORD)]

class IEnumConnections(IUnknown):
    _iid_ = GUID("{B196B287-BAB4-101A-B69C-00AA00341D07}")
PIEnumConnections = POINTER(IEnumConnections)

class IEnumConnectionPoints(IUnknown):
    _iid_ = GUID("{B196B285-BAB4-101A-B69C-00AA00341D07}")
PIEnumConnectionPoints = POINTER(IEnumConnectionPoints)

class IConnectionPointContainer(IUnknown):
    _iid_ = GUID("{B196B284-BAB4-101A-B69C-00AA00341D07}")
PIConnectionPointContainer = POINTER(IConnectionPointContainer)

class IConnectionPoint(IUnknown):
    _iid_ = GUID("{B196B286-BAB4-101A-B69C-00AA00341D07}")
PIConnectionPoint = POINTER(IConnectionPoint)

################

IEnumConnections._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Next", c_ulong, POINTER(CONNECTDATA), POINTER(c_ulong)),
    STDMETHOD(HRESULT, "Skip", c_ulong),
    STDMETHOD(HRESULT, "Reset"),
    STDMETHOD(HRESULT, "Clone", POINTER(PIEnumConnections))]

IEnumConnectionPoints._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Next", c_ulong, POINTER(IConnectionPoint), POINTER(c_ulong)),
    STDMETHOD(HRESULT, "Skip", c_ulong),
    STDMETHOD(HRESULT, "Reset"),
    STDMETHOD(HRESULT, "Clone", POINTER(PIEnumConnectionPoints))]

IConnectionPoint._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "GetConnectionInterface", POINTER(GUID)),
    STDMETHOD(HRESULT, "GetConnectionPointContainer", POINTER(PIConnectionPointContainer)),
    STDMETHOD(HRESULT, "Advise", POINTER(IUnknown), POINTER(DWORD)),
    STDMETHOD(HRESULT, "Unadvise", DWORD),
    STDMETHOD(HRESULT, "EnumConnections", POINTER(PIEnumConnections))]

IConnectionPointContainer._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "EnumConnectionPoints", POINTER(PIEnumConnectionPoints)),
    STDMETHOD(HRESULT, "FindConnectionPoint", REFIID, POINTER(PIConnectionPoint))]

