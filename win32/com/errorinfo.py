from ctypes import *
from ctypes.wintypes import LPOLESTR
from ctypes.com import IUnknown, GUID, STDMETHOD, HRESULT
from ctypes.com.automation import BSTR, oleaut32, BSTR
from ctypes.com.hresult import S_FALSE, S_OK

class ICreateErrorInfo(IUnknown):
    _iid_ = GUID("{22F03340-547D-101B-8E65-08002B2BD119}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "SetGUID", POINTER(GUID)),
        STDMETHOD(HRESULT, "SetSource", LPOLESTR),
        STDMETHOD(HRESULT, "SetDescription", LPOLESTR),
        STDMETHOD(HRESULT, "SetHelpFile", LPOLESTR),
        STDMETHOD(HRESULT, "SetHelpContext", LPOLESTR),
        ]

class IErrorInfo(IUnknown):
    _iid_ = GUID("{1CF2B120-547D-101B-8E65-08002B2BD119}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "GetGUID", POINTER(GUID)),
        STDMETHOD(HRESULT, "GetSource", POINTER(BSTR)),
        STDMETHOD(HRESULT, "GetDescription", POINTER(BSTR)),
        STDMETHOD(HRESULT, "GetHelpFile", POINTER(BSTR)),
        STDMETHOD(HRESULT, "GetHelpContext", POINTER(BSTR)),
        ]


def CreateErrorInfo():
    cei = POINTER(ICreateErrorInfo)()
    oleaut32.CreateErrorInfo(byref(cei))
    return cei

def GetErrorInfo():
    errinfo = POINTER(IErrorInfo)()
    if S_OK == oleaut32.GetErrorInfo(0, byref(errinfo)):
        return errinfo
    return None

def SetErrorInfo(errinfo):
    return oleaut32.SetErrorInfo(0, errinfo)

################################################################

if __name__ == "__main__":
    def doit():
        for i in range(10):
            cei = CreateErrorInfo()
            cei.SetSource(u"Spam, spam, and spam")

            SetErrorInfo(cei)

            ei = GetErrorInfo()
            src = BSTR()
            ei.GetSource(byref(src))

            oleaut32.SysAllocString(u"aber halle")

    from mallocspy import MallocSpy

    mallocspy = MallocSpy()
    mallocspy.register()

    doit()

    import ctypes.com
    windll.ole32.CoUninitialize()
    print "Clean"

    mallocspy.revoke()
    print "Done"

##    ctypes.com.__cleaner = None
