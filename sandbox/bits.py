from ctypes import *
from binascii import hexlify

class X(Structure):
    _fields_ = [("a", c_longlong, 1),
                ("b", c_longlong, 1),
                ("c", c_longlong, 1),
                ("d", c_longlong, 1),
                ("e", c_longlong, 1),
                ("f", c_longlong, 1),
                ("g", c_longlong, 1),
                ("h", c_longlong, 1),
                ("i", c_longlong, 1),
                ("j", c_longlong, 1),
                ("k", c_longlong, 1),
                ("l", c_longlong, 1),
                ("m", c_longlong, 1),
                ("n", c_longlong, 1),
                ("o", c_longlong, 1),
                ("p", c_longlong, 1),
                ("q", c_longlong, 1),
                ("r", c_longlong, 1),
                ("s", c_longlong, 1),
                ("t", c_longlong, 1),
                ("u", c_longlong, 1),
                ("v", c_longlong, 1),
                ("w", c_longlong, 1),
                ("x", c_longlong, 1),
                ("y", c_longlong, 1),
                ("z", c_longlong, 1)]

x = X()

for n in "abcdefghijklmnopqrstuvwyxz":
    setattr(x, n, -1)
    print hexlify(buffer(x))
