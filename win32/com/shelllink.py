# -*- coding: latin-1 -*-
from ctypes import *
from ctypes.com import IUnknown, STDMETHOD, HRESULT, GUID, ole32
from ctypes.wintypes import WORD, DWORD, FILETIME, LPSTR, LPCSTR, LPWSTR, LPCWSTR, HWND, WIN32_FIND_DATAA

class SHITEMID(Structure):
    _fields_ = [("cb", c_ushort),
                ("abID", c_ubyte * 1)] # variable length, in reality

class ITEMIDLIST(Structure):
    _fields_ = [("mkid", SHITEMID)]

class IShellLinkA(IUnknown):
    _iid_ = GUID("{000214EE-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "GetPath", LPSTR, c_int, POINTER(WIN32_FIND_DATAA), DWORD),
        STDMETHOD(HRESULT, "GetIDList", POINTER(ITEMIDLIST)),
        STDMETHOD(HRESULT, "SetIDList",  POINTER(ITEMIDLIST)),
        STDMETHOD(HRESULT, "GetDescription", LPSTR, c_int),
        STDMETHOD(HRESULT, "SetDescription", LPCSTR),
        STDMETHOD(HRESULT, "GetWorkingDirectory", LPSTR, c_int),
        STDMETHOD(HRESULT, "SetWorkingDirectory", LPCSTR),
        STDMETHOD(HRESULT, "GetArguments", LPSTR, c_int),
        STDMETHOD(HRESULT, "SetArguments", LPCSTR),
        STDMETHOD(HRESULT, "GetHotkey", POINTER(WORD)),
        STDMETHOD(HRESULT, "SetHotkey", WORD),
        STDMETHOD(HRESULT, "GetShowCmd", POINTER(c_int)),
        STDMETHOD(HRESULT, "SetShowCmd", c_int),
        STDMETHOD(HRESULT, "GetIconLocation", LPSTR, c_int, POINTER(c_int)),
        STDMETHOD(HRESULT, "SetIconLocation", LPCSTR, c_int),
        STDMETHOD(HRESULT, "SetRelativePath", LPCSTR, DWORD),
        STDMETHOD(HRESULT, "Resolve", HWND, DWORD),
        STDMETHOD(HRESULT, "SetPath", LPCSTR)
        ]

CLSID_ShellLink = GUID("{00021401-0000-0000-C000-000000000046}")

class IShellLinkW(IUnknown):
    _iid_ = GUID("{000214F9-0000-0000-C000-000000000046}")
    _methods_ = IUnknown._methods_ + [
        STDMETHOD(HRESULT, "GetPath", LPWSTR, c_int, POINTER(WIN32_FIND_DATAA), DWORD),
        STDMETHOD(HRESULT, "GetIDList", POINTER(ITEMIDLIST)),
        STDMETHOD(HRESULT, "SetIDList",  POINTER(ITEMIDLIST)),
        STDMETHOD(HRESULT, "GetDescription", LPWSTR, c_int),
        STDMETHOD(HRESULT, "SetDescription", LPCWSTR),
        STDMETHOD(HRESULT, "GetWorkingDirectory", LPWSTR, c_int),
        STDMETHOD(HRESULT, "SetWorkingDirectory", LPCWSTR),
        STDMETHOD(HRESULT, "GetArguments", LPWSTR, c_int),
        STDMETHOD(HRESULT, "SetArguments", LPCWSTR),
        STDMETHOD(HRESULT, "GetHotkey", POINTER(WORD)),
        STDMETHOD(HRESULT, "SetHotkey", WORD),
        STDMETHOD(HRESULT, "GetShowCmd", POINTER(c_int)),
        STDMETHOD(HRESULT, "SetShowCmd", c_int),
        STDMETHOD(HRESULT, "GetIconLocation", LPWSTR, c_int, POINTER(c_int)),
        STDMETHOD(HRESULT, "SetIconLocation", LPCWSTR, c_int),
        STDMETHOD(HRESULT, "SetRelativePath", LPCWSTR, DWORD),
        STDMETHOD(HRESULT, "Resolve", HWND, DWORD),
        STDMETHOD(HRESULT, "SetPath", LPCWSTR)
        ]

if __debug__:
    if __name__ == "__main__":
        from ctypes.com.persist import IPersistFile
        from ctypes.com import CLSCTX_INPROC_SERVER
        p = POINTER(IShellLinkA)()
        ole32.CoCreateInstance(byref(CLSID_ShellLink),
                               0,
                               CLSCTX_INPROC_SERVER,
                               byref(IShellLinkA._iid_),
                               byref(p))
        print p
        p.SetPath(r"c:\windows\system32\notepad.exe")
        p.SetDescription("Notepad Würg Röchel")
        p.SetArguments("c:\windows\upgrade.txt")
        p.SetWorkingDirectory("c:\\")


        pp = POINTER(IPersistFile)()
        p.QueryInterface(byref(IPersistFile._iid_), byref(pp))
        print pp.Save(ur"c:\XXX.lnk", True)

