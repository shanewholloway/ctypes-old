# ctypes client code, using the CSum COM object
##import pywintypes

from ctypes import *
from ctypes.com import CreateInstance
from ctypes.com.automation import IDispatch
from sum_gen import CSum

CLSCTX_INPROC_SERVER = 0x1
CLSCTX_LOCAL_SERVER = 0x4

import sys
if "inproc_server" in sys.argv:
    print "Using CLSCTX_INPROC_SERVER"
    clsctx = CLSCTX_INPROC_SERVER
else:
    print "Using CLSCTX_LOCAL_SERVER"
    clsctx = CLSCTX_LOCAL_SERVER

sum = CreateInstance(CSum, clsctx=clsctx)
result = c_double()
sum.Add(3.14, 3.14, byref(result))
print "Added 3.14 and 3.14, result", result.value

idisp = pointer(IDispatch())

sum.QueryInterface(byref(IDispatch._iid_), byref(idisp))

count = c_uint()
idisp.GetTypeInfoCount(byref(count))
print "Has Typeinfo?", count.value

del idisp
print "After del idisp"
import gc
gc.collect()

print "After gc.collect()"
