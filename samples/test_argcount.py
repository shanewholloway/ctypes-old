from ctypes import c_char, c_string, byref, cdll, c_int

import os
if os.name == "nt":
    strchr = cdll.msvcrt.strchr
elif os.name == "posix":
    strchr = cdll.LoadLibrary("/lib/libc.so.6").strchr

strchr.restype = "s"
strchr.argtypes = [c_string, c_int]

try:
    strchr(1, 2, 3)
except ValueError:
    pass
else:
    raise Error("didn't catch wrong number of args")

try:
    strchr()
except ValueError:
    pass
else:
    raise Error("didn't catch wrong number of args")

strchr.restype = "s"
strchr.argtypes = [c_string, c_int]
assert "def" ==  strchr("abcdef", ord("d"))
assert None == strchr("abcdef", ord("x"))

strchr.argtypes = [c_string, c_char]
assert None == strchr("abcdef", "x")
assert "def" == strchr("abcdef", "d")
