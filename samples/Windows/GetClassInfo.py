# This sample demonstrates ...

from ctypes import *
from ctypes.wintypes import HINSTANCE, HANDLE

HICON = HANDLE
HCURSOR = HANDLE
HICON = HANDLE
HBRUSH = HANDLE

LPCTSTR = c_char_p

WNDPROC = WINFUNCTYPE(c_int, c_int, c_int, c_int, c_int)

class WNDCLASS(Structure):
    _fields_ = [("style", c_uint),
                ("lpfnWndProc", WNDPROC),
                ("cbClsExtra", c_int),
                ("cbWndExtra", c_int),
                ("hInstance", HINSTANCE),
                ("hIcon", HICON),
                ("hCursor", HCURSOR),
                ("hbrBackground", HBRUSH),
                ("lpszMenuName", LPCTSTR),
##                ("lpszClassName", POINTER(c_char))]
                ("lpszClassName", LPCTSTR)]

wndclass = WNDCLASS()


windll.user32.GetClassInfoA(None, "Edit", byref(wndclass))
for name, tp in wndclass._fields_:
    print name, repr(getattr(wndclass, name))
##print "lpszClassName", wndclass.lpszClassName[0]
##print "lpszClassName", wndclass.lpszClassName[1]

##wndclass.lpszClassName = c_buffer("HIHI")
##print "lpszClassName", wndclass.lpszClassName[0]
##print "lpszClassName", wndclass.lpszClassName[1]
