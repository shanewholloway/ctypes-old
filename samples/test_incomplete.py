from ctypes import *

lpcell = POINTER("cell")
class cell(Structure):
    _fields_ = [("name", c_char_p),
                ("next", lpcell)]

SetPointerType(lpcell, cell)

c1 = cell()
c1.name = "foo"
c2 = cell()
c2.name = "bar"

c1.next = pointer(c2)
c2.next = pointer(c1)

p = c1

for i in range(8):
    print p.name,
    p = p.next[0]
