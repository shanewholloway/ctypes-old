# ctypes client code, using the CSum COM object
from ctypes import *
from ctypes.com import IUnknown, ole32, GUID

CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4

clsid = GUID('{d0329e37-14c1-4d71-a4d8-df9534c7ebdf}')
p = pointer(IUnknown())

import sys
if "inproc_server" in sys.argv:
    print "Using CLSCTX_INPROC_SERVER"
    clsctx = CLSCTX_INPROC_SERVER
    # XXX to avoid a crash in pywintypes, we have to import pywintypes
    # before using a win32com implemented inproc server.
    import pywintypes
else:
    print "Using CLSCTX_LOCAL_SERVER"
    clsctx = CLSCTX_LOCAL_SERVER

ole32.CoCreateInstance(byref(clsid),
                       0,
                       clsctx,
                       byref(IUnknown._iid_),
                       byref(p))

assert((2, 1) == (p.AddRef(), p.Release()))
