# storage interfaces
from ctypes import *
from ctypes.com import IUnknown, GUID, HRESULT, STDMETHOD
from ctypes.wintypes import DWORD
from ctypes.com import ole32

LPOLESTR = LPCOLESTR = c_wchar_p
BOOL = c_int
LARGE_INTEGER = c_longlong
ULARGE_INTEGER = c_ulonglong

class FILETIME(Structure):
    _fields_ = [("dwLowDateTime", DWORD),
                ("dwHighDateTime", DWORD)]

class STATSTG(Structure):
    _fields_ = [("pwcsName", LPOLESTR),
                ("type", DWORD),
                ("cbSize", ULARGE_INTEGER),
                ("mtime", FILETIME),
                ("ctime", FILETIME),
                ("atime", FILETIME),
                ("grfMode", DWORD),
                ("grfLocksSupported", DWORD),
                ("clsid", GUID),
                ("grfStateBits", DWORD),
                ("reserved", DWORD)]

STGTY_STORAGE   = 1
STGTY_STREAM    = 2
STGTY_LOCKBYTES = 3
STGTY_PROPERTY  = 4

STREAM_SEEK_SET = 0
STREAM_SEEK_CUR = 1
STREAM_SEEK_END = 2

LOCK_WRITE      = 1
LOCK_EXCLUSIVE  = 2
LOCK_ONLYONCE   = 4

class ISequentialStream(IUnknown):
    _iid_ = GUID("{0c733a30-2a1c-11ce-ade5-00aa0044773d}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "Read", c_voidp, c_ulong, POINTER(c_ulong)),
        STDMETHOD(HRESULT, "Write", c_voidp, c_ulong, POINTER(c_ulong)),
        ]

class IStream(ISequentialStream):
    _iid_ = GUID("{0000000C-0000-0000-C000-000000000046}")

IStream._methods_ = ISequentialStream._methods_ + [
    STDMETHOD(HRESULT, "Seek", LARGE_INTEGER, DWORD, POINTER(ULARGE_INTEGER)),
    STDMETHOD(HRESULT, "SetSize", ULARGE_INTEGER),
    STDMETHOD(HRESULT, "CopyTo", POINTER(IStream), ULARGE_INTEGER,
              POINTER(ULARGE_INTEGER), POINTER(ULARGE_INTEGER)),
    STDMETHOD(HRESULT, "Commit", DWORD),
    STDMETHOD(HRESULT, "Revert"),
    STDMETHOD(HRESULT, "LockRegion", ULARGE_INTEGER, ULARGE_INTEGER, DWORD),
    STDMETHOD(HRESULT, "UnlockRegion", ULARGE_INTEGER, ULARGE_INTEGER, DWORD),
    STDMETHOD(HRESULT, "Stat", POINTER(STATSTG), DWORD),
    STDMETHOD(HRESULT, "Clone", POINTER(POINTER(IStream)))]

def CoMarshalInterThreadInterfaceInStream(punk, iid=None):
    if iid is None:
        iid = punk[0]._iid_
    pstream = POINTER(IStream)()
    ole32.CoMarshalInterThreadInterfaceInStream(byref(iid), punk, byref(pstream))
    return pstream

def CoGetInterfaceAndReleaseStream(pstm, interface, iid=None):
    if iid is None:
        iid = interface._iid_
    result = POINTER(interface)()
    pstm.AddRef()
    # CoGetInterfaceAndReleaseStream will call Release(), but ctypes does it
    # automatically when pstm is deleted!
    ole32.CoGetInterfaceAndReleaseStream(pstm, byref(iid), byref(result))
    return result

##__all__ = []

if __debug__:
    if __name__ == "__main__":
        from ctypes.com import CLSCTX_INPROC_SERVER, CLSCTX_LOCAL_SERVER
        from ctypes.com.automation import IDispatch
        # InternetExplorer.Application
        clsid = GUID("{0002DF01-0000-0000-C000-000000000046}")
        punk = POINTER(IDispatch)()
        ole32.CoCreateInstance(byref(clsid),
                               None,
                               CLSCTX_INPROC_SERVER | CLSCTX_LOCAL_SERVER,
                               byref(IDispatch._iid_),
                               byref(punk))
        stm = CoMarshalInterThreadInterfaceInStream(punk)

        def run_in_thread():
            print "IN THREAD 1"
            from ctypes.com import ole32
            ole32.CoInitialize(0)
            p = CoGetInterfaceAndReleaseStream(stm, IDispatch)
            print p.AddRef(), p.Release()
            import time
            time.sleep(1)
            print p.AddRef(), p.Release()
            print "IN THREAD 2"
            ole32.CoUninitialize()

        import threading
        t = threading.Thread(target = run_in_thread)
        t.start()
        t.join()
