from ctypes import c_ulong, POINTER, byref, c_void_p, c_wchar_p, Structure
from ctypes.wintypes import DWORD, BOOL, FILETIME, LCID, ULONG, LPOLESTR
from ctypes.com import CreateInstance, GUID, ole32, IUnknown, STDMETHOD, HRESULT, REFIID
from ctypes.com.persist import IPersistStream

class BIND_OPTS(Structure):
    _fields_ = [("cbStruct", DWORD),
                ("grfFlags", DWORD),
                ("grfMode", DWORD),
                ("dwTickCountDeadline", DWORD)]

# BIND_OPTS2 can be used instead of BIND_OPTS.  But BIND_OPTS2
# requires a lot of other structure definitions, and we don't need
# this now.  When BIND_OPTS2 is defined, make sure to define a
# BIND_OPTS.from_parameter class method, which will accept BIND_OPTS2
# instances as well.

################################################################

class IRunningObjectTable(IUnknown):
    _iid_ = GUID("{00000010-0000-0000-C000-000000000046}")

class IEnumString(IUnknown):
    _iid_ = GUID("{00000101-0000-0000-C000-000000000046}")

class IEnumMoniker(IUnknown):
    _iid_ = GUID("{00000102-0000-0000-C000-000000000046}")

class IBindCtx(IUnknown):
    _iid_ = GUID("{0000000E-0000-0000-C000-000000000046}")

class IMoniker(IPersistStream):
    _iid_ = GUID("{0000000F-0000-0000-C000-000000000046}")

################################

IRunningObjectTable._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Register", DWORD, POINTER(IUnknown), POINTER(IMoniker), POINTER(DWORD)),
    STDMETHOD(HRESULT, "Revoke", DWORD),
    STDMETHOD(HRESULT, "IsRunning", POINTER(IMoniker)),
    STDMETHOD(HRESULT, "GetObject", POINTER(IMoniker), POINTER(POINTER(IUnknown))),
    STDMETHOD(HRESULT, "NoteChangeTime", DWORD, POINTER(FILETIME)),
    STDMETHOD(HRESULT, "GetTimeOfLastChange", POINTER(IMoniker), POINTER(FILETIME)),
    STDMETHOD(HRESULT, "EnumRunning", POINTER(POINTER(IEnumMoniker)))]

IEnumString._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Next", c_ulong, POINTER(LPOLESTR), POINTER(c_ulong)),
    STDMETHOD(HRESULT, "Skip", c_ulong),
    STDMETHOD(HRESULT, "Reset"),
    STDMETHOD(HRESULT, "Clone", POINTER(POINTER(IEnumString)))
    ]

IEnumMoniker._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "Next", c_ulong, POINTER(POINTER(IMoniker)), POINTER(c_ulong)),
    STDMETHOD(HRESULT, "Skip", c_ulong),
    STDMETHOD(HRESULT, "Reset"),
    STDMETHOD(HRESULT, "Clone", POINTER(POINTER(IEnumMoniker)))
    ]

IBindCtx._methods_ = IUnknown._methods_ + [
    STDMETHOD(HRESULT, "RegisterObjectBound", POINTER(IUnknown)),
    STDMETHOD(HRESULT, "RevokeObjectBound", POINTER(IUnknown)),
    STDMETHOD(HRESULT, "ReleaseBoundObjects"),
    STDMETHOD(HRESULT, "SetBindOptions", POINTER(BIND_OPTS)),
    STDMETHOD(HRESULT, "GetBindOptions", POINTER(BIND_OPTS)),
    STDMETHOD(HRESULT, "GetRunningObjectTable", POINTER(POINTER(IRunningObjectTable))),
    STDMETHOD(HRESULT, "RegisterObjectParam", LPOLESTR, POINTER(IUnknown)),
    STDMETHOD(HRESULT, "GetObjectParam", LPOLESTR, POINTER(POINTER(IUnknown))),
    STDMETHOD(HRESULT, "EnumObjectParam", POINTER(POINTER(IEnumString))),
    STDMETHOD(HRESULT, "RevokeObjectParam", LPOLESTR)]

IMoniker._methods_ = IPersistStream._methods_ + [
    STDMETHOD(HRESULT, "BindToObject", POINTER(IBindCtx), POINTER(IMoniker), REFIID, c_void_p),
    STDMETHOD(HRESULT, "BindToStorage", POINTER(IBindCtx), POINTER(IMoniker), REFIID, c_void_p),
    STDMETHOD(HRESULT, "Reduce", POINTER(IBindCtx), DWORD,
              POINTER(POINTER(IMoniker)), POINTER(POINTER(IMoniker))),
    STDMETHOD(HRESULT, "ComposeWith", POINTER(IMoniker), BOOL, POINTER(POINTER(IMoniker))),
    STDMETHOD(HRESULT, "Enum", BOOL, POINTER(IEnumMoniker)),
    STDMETHOD(HRESULT, "IsEqual", POINTER(IMoniker)),
    STDMETHOD(HRESULT, "Hash", POINTER(DWORD)),
    STDMETHOD(HRESULT, "IsRunning", POINTER(IBindCtx), POINTER(IMoniker), POINTER(IMoniker)),
    STDMETHOD(HRESULT, "GetTimeOfLastChange", POINTER(IBindCtx), POINTER(IMoniker),
              POINTER(FILETIME)),
    STDMETHOD(HRESULT, "Inverse", POINTER(IMoniker)),
    STDMETHOD(HRESULT, "CommonPrefixWith", POINTER(IMoniker), POINTER(POINTER(IMoniker))),
    STDMETHOD(HRESULT, "RelativePathTo", POINTER(IMoniker), POINTER(POINTER(IMoniker))),
    STDMETHOD(HRESULT, "GetDisplayName", POINTER(IBindCtx), POINTER(IMoniker), POINTER(LPOLESTR)),
    STDMETHOD(HRESULT, "ParseDisplayName", POINTER(IBindCtx), POINTER(IMoniker),
              LPOLESTR, POINTER(ULONG), POINTER(POINTER(IMoniker))),
    STDMETHOD(HRESULT, "IsSystemMoniker", POINTER(DWORD))]

################################################################

def CreateBindContext():
    bc = POINTER(IBindCtx)()
    ole32.CreateBindCtx(0, byref(bc))
    return bc

def MkParseDisplayName(displayName, bindCtx=None):
    if bindCtx is None:
        bindCtx = CreateBindContext()
    moniker = POINTER(IMoniker)()
    chEaten = c_ulong()
    ole32.MkParseDisplayName(bindCtx,
                             unicode(displayName),
                             byref(chEaten),
                             byref(moniker))
    # That's what win32com returns:
    return moniker, chEaten.value, bindCtx
