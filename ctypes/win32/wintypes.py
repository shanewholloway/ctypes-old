from ctypes import *

DWORD = c_ulong
WORD = c_ushort
BYTE = c_byte

LARGE_INTEGER = c_longlong
ULARGE_INTEGER = c_ulonglong


HANDLE = c_ulong # in the header files: void *

HWND = HANDLE
HDC = HANDLE
HMODULE = HANDLE
HINSTANCE = HANDLE
HRGN = HANDLE
HTASK = HANDLE
HKEY = HANDLE
HPEN = HANDLE
HGDIOBJ = HANDLE
HMENU = HANDLE

WPARAM = c_uint
LPARAM = c_long

BOOL = c_long
VARIANT_BOOL = c_short

LPCOLESTR = LPOLESTR = OLESTR = c_wchar_p
LPCWSTR = LPWSTR = c_wchar_p

LPCSTR = LPSTR = c_char_p

class RECT(Structure):
    _fields_ = [("left", c_long),
                ("top", c_long),
                ("right", c_long),
                ("bottom", c_long)]
RECTL = RECT

class POINT(Structure):
    _fields_ = [("x", c_long),
                ("y", c_long)]
POINTL = POINT

class SIZE(Structure):
    _fields_ = [("cx", c_long),
                ("cy", c_long)]
SIZEL = SIZE

def RGB(red, green, blue):
    return red + (green << 8) + (blue << 16)

class FILETIME(Structure):
    _fields_ = [("dwLowDateTime", DWORD),
                ("dwHighDateTime", DWORD)]

class MSG(Structure):
    _fields_ = [("hWnd", HWND),
                ("message", c_uint),
                ("wParam", WPARAM),
                ("lParam", LPARAM),
                ("time", DWORD),
                ("pt", POINT)]
MAX_PATH = 260

# there's also a unicode version of that
class WIN32_FIND_DATAA(Structure):
    _fields_ = [("dwFileAttributes", DWORD),
                ("ftCreationTime", FILETIME),
                ("ftLastAccessTime", FILETIME),
                ("ftLastWriteTime", FILETIME),
                ("nFileSizeHigh", DWORD),
                ("nFileSizeLow", DWORD),
                ("dwReserved0", DWORD),
                ("dwReserved1", DWORD),
                ("cFileName", c_char * MAX_PATH),
                ("cAlternameFileName", c_char * 14)]
