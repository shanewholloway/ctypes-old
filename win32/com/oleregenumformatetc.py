from ctypes import *
from ctypes.com import GUID

ole32 = windll.ole32
ole32 = oledll.ole32

DATADIR_GET = 1
DATADIR_SET = 2

p = c_int()

print hex(ole32.OleRegEnumFormatEtc(byref(GUID("{00000402-0000-0000-C000-000000000046}")),
                                1,
                                byref(p)))

print p
