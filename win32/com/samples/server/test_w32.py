# win32com client code to use the CSum COM object

import sys

CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4

import sys
if "inproc_server" in sys.argv:
    print "Using CLSCTX_INPROC_SERVER"
    clsctx = CLSCTX_INPROC_SERVER
else:
    print "Using CLSCTX_LOCAL_SERVER"
    clsctx = CLSCTX_LOCAL_SERVER

from win32com.client import Dispatch
d = Dispatch("ctypes.SumObject", clsctx=clsctx)
assert 6.28 == d.Add(3.14, 3.14)
