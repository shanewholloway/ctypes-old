import sys, re

# Some preformance measurements
def timeit(*args):
    from timeit import main
    from cStringIO import StringIO

    prev_stdout = sys.stdout
    sys.stdout = StringIO()

    main(args)

    out = sys.stdout.getvalue()
    sys.stdout = prev_stdout
    match = re.search(r"(\d+\.\d*|\d+) usec", out)
    time = float(match.group(1))
    print "%8.2f: %s" % (time, args[-1])

################################################################
import ctypes
from ctypes import *
class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]

class RECT(Structure):
    _fields_ = [("ul", POINT), ("lr", POINT)]

class Class(object):
    pass

# get a FUNCDESC instance
from ctypes.com.client import Dispatch
d = Dispatch("InternetExplorer.Application")
fd = d.Navigate.fd

################################################################

if __name__ == "__main__":
    print "ctypes version:", ctypes.__version__
    print "python version:", sys.version

    timeit("-s", "from test_perf import Class",
         "Class()")
    timeit("-s", "from test_perf import POINT",
         "POINT()")
    timeit("-s", "from test_perf import RECT",
         "RECT()")
    timeit("-s", "from test_perf import POINT; point = POINT()",
         "point.y")
    timeit("-s", "from test_perf import RECT; rect = RECT()",
         "rect.lr")
    timeit("-s", "from test_perf import fd",
         "fd.lprgelemdescParam")
    timeit("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[0]")
    timeit("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1]")
    timeit("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1].tdesc")
    timeit("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1].tdesc.vt")
    timeit("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1].tdesc.u.lptdesc[0].vt")
    timeit('-s', "from ctypes import c_int",
           "c_int()")
    timeit('-s', "from ctypes import c_int",
           "c_int(42)")
    timeit('-s', "from ctypes.com.automation import VARIANT",
           "VARIANT()                                   # ctypes.com")
    timeit('-s', "from ctypes.com.automation import VARIANT; variant = VARIANT(3)",
           "variant.value                               # ctypes.com")
    timeit('-s', "from ctypes.com.automation import VARIANT; variant = VARIANT()",
           "variant.value = 3.14                        # ctypes.com")
    try:
        import comtypes
    except ImportError:
        sys.exit()

    timeit('-s', "from comtypes.automation import VARIANT",
           "VARIANT()                                   # comtypes")
    timeit('-s', "from comtypes.automation import VARIANT; variant = VARIANT(3)",
           "variant.value                               # comtypes")
    timeit('-s', "from comtypes.automation import VARIANT; variant = VARIANT()",
           "variant.value = 3.14                        # comtypes")

# on my machine:

##ctypes version: 0.9.2
##python version: 2.4 (#60, Nov 30 2004, 11:49:19) [MSC v.1310 32 bit (Intel)]
##    0.38: Class()
##    1.97: POINT()
##    1.98: RECT()
##    0.24: point.y
##    2.43: rect.lr
##    7.21: fd.lprgelemdescParam
##   10.90: fd.lprgelemdescParam[0]
##   12.00: fd.lprgelemdescParam[1]
##   15.30: fd.lprgelemdescParam[1].tdesc
##   16.00: fd.lprgelemdescParam[1].tdesc.vt
##   26.20: fd.lprgelemdescParam[1].tdesc.u.lptdesc[0].vt
##    1.80: c_int()
##    1.97: c_int(42)
##    2.93: VARIANT()                                   # ctypes.com
##    5.30: variant.value                               # ctypes.com
##   11.60: variant.value = 3.14                        # ctypes.com


##ctypes version: 0.9.3
##python version: 2.4 (#60, Nov 30 2004, 11:49:19) [MSC v.1310 32 bit (Intel)]
##    0.41: Class()
##    1.34: POINT()
##    1.39: RECT()
##    0.23: point.y
##    2.36: rect.lr
##    7.22: fd.lprgelemdescParam
##   10.80: fd.lprgelemdescParam[0]
##   10.90: fd.lprgelemdescParam[1]
##   13.50: fd.lprgelemdescParam[1].tdesc
##   14.40: fd.lprgelemdescParam[1].tdesc.vt
##   21.70: fd.lprgelemdescParam[1].tdesc.u.lptdesc[0].vt
##    1.13: c_int()
##    1.32: c_int(42)
##    2.34: VARIANT()                                   # ctypes.com
##    5.49: variant.value                               # ctypes.com
##   11.60: variant.value = 3.14                        # ctypes.com
##    1.40: VARIANT()                                   # comtypes
##    5.54: variant.value                               # comtypes
##   12.10: variant.value = 3.14                        # comtypes
