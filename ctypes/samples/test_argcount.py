from ctypes import c_char, byref, cdll, c_int, c_char_p

import os, sys
if os.name == "nt":
    strchr = cdll.msvcrt.strchr
elif os.name == "posix":
    if sys.platform == "darwin":
        strchr = cdll.LoadLibrary("/usr/lib/libc.dylib").strchr
    elif sys.platform == "cygwin":
        strchr = cdll.LoadLibrary("/bin/cygwin1.dll").strchr
    else:
        strchr = cdll.LoadLibrary("/lib/libc.so.6").strchr

strchr.restype = c_char_p
strchr.argtypes = [c_char_p, c_int]

try:
    strchr("abc", 2, 3)
except TypeError:
    pass
else:
    raise Exception("didn't catch wrong number of args")

try:
    strchr()
except TypeError:
    pass
else:
    raise ("didn't catch wrong number of args")

strchr.restype = c_char_p
strchr.argtypes = [c_char_p, c_int]
assert "def" ==  strchr("abcdef", ord("d"))
assert None == strchr("abcdef", ord("x"))

strchr.argtypes = [c_char_p, c_char]
assert None == strchr("abcdef", "x")
assert "def" == strchr("abcdef", "d")
