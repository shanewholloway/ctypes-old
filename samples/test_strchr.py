from ctypes import c_char, byref, cdll, c_int, c_char_p

import os, sys
if os.name == "nt":
    strchr = cdll.msvcrt.strchr
elif os.name == "posix":
    if sys.platform == "darwin":
        strchr = cdll.LoadLibrary("/usr/lib/libc.dylib").strchr
    else:
        strchr = cdll.LoadLibrary("/lib/libc.so.6").strchr

strchr.restype = c_char_p # "z"

strchr.argtypes = [c_char_p, c_int]

assert "def" ==  strchr("abcdef", ord("d"))
assert None == strchr("abcdef", ord("x"))

strchr.argtypes = [c_char_p, c_char]
assert None == strchr("abcdef", "x")
assert "def" == strchr("abcdef", "d")
