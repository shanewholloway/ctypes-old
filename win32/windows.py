from ctypes import Structure, \
     c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint, \
     c_long, c_ulong, c_longlong, c_ulonglong, \
     c_char_p, c_wchar_p

DWORD = c_ulong
WORD = c_ushort
BYTE = c_byte

HANDLE = c_ulong # in the header files: void *

HWND = HANDLE
HMODULE = HANDLE
HINSTANCE = HANDLE
HRGN = HANDLE
HTASK = HANDLE
HKEY = HANDLE
HPEN = HANDLE
HGDIOBJ = HANDLE

WPARAM = c_uint
LPARAM = c_long

OLESTR = c_wchar_p

class RECT(Structure):
    _fields_ = [("left", c_long),
                ("top", c_long),
                ("right", c_long),
                ("bottom", c_long)]

class POINT(Structure):
    _fields_ = [("x", c_long),
                ("y", c_long)]

class MSG(Structure):
    _fields_ = [("hwnd", HWND),
                ("message", c_uint),
                ("wParam", WPARAM),
                ("lParam", LPARAM),
                ("time", DWORD),
                ("pt", POINT)]
