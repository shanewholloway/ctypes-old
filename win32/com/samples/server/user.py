# ctypes client code, using the CSum COM object
from ctypes import *
from ctypes.com import IUnknown, ole32, GUID

CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4

clsid = GUID('{2E0504A1-1A23-443F-939D-869A6C731521}')
p = pointer(IUnknown())

import sys
if "inproc_server" in sys.argv:
    print "Using CLSCTX_INPROC_SERVER"
    clsctx = CLSCTX_INPROC_SERVER
else:
    print "Using CLSCTX_LOCAL_SERVER"
    clsctx = CLSCTX_LOCAL_SERVER

ole32.CoCreateInstance(byref(clsid),
                       0,
                       clsctx,
                       byref(IUnknown._iid_),
                       byref(p))

assert((2, 1) == (p.AddRef(), p.Release()))
