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

class ClassWithInit(object):
    def __init__(self):
        pass

def get_fd():
    # get a FUNCDESC instance
##    from ctypes.com.client import Dispatch
##    d = Dispatch("InternetExplorer.Application")
##    return d.Navigate.fd
    # no longer from a 'live' IE object, from the typelib instead
    from comtypes.typeinfo import LoadTypeLibEx
    from comtypes import GUID
    tlib = LoadTypeLibEx("shdocvw.dll")
    # IWebBrowser interface
    tinfo = tlib.GetTypeInfoOfGuid(GUID("{EAB22AC1-30C1-11CF-A7EB-0000C05BAE0B}"))
    tcomp = tinfo.GetTypeComp()
    kind, fd = tcomp.Bind("Navigate")
    return fd

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
    timeit("-s", "from test_perf import get_fd; fd = get_fd()",
         "fd.lprgelemdescParam")
    timeit("-s", "from test_perf import get_fd; fd = get_fd()",
         "fd.lprgelemdescParam[0]")
    timeit("-s", "from test_perf import get_fd; fd = get_fd()",
         "fd.lprgelemdescParam[1]")
    timeit("-s", "from test_perf import get_fd; fd = get_fd()",
         "fd.lprgelemdescParam[1].tdesc")
    timeit("-s", "from test_perf import get_fd; fd = get_fd()",
         "fd.lprgelemdescParam[1].tdesc.vt")
    timeit("-s", "from test_perf import get_fd; fd = get_fd()",
         "fd.lprgelemdescParam[1].tdesc._.lptdesc[0].vt")
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
        pass
    else:

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
##    0.37: Class()
##    0.96: POINT()
##    0.94: RECT()
##    0.25: point.y
##    1.94: rect.lr
##    7.16: fd.lprgelemdescParam
##   10.10: fd.lprgelemdescParam[0]
##   10.00: fd.lprgelemdescParam[1]
##   12.30: fd.lprgelemdescParam[1].tdesc
##   13.70: fd.lprgelemdescParam[1].tdesc.vt
##   19.30: fd.lprgelemdescParam[1].tdesc.u.lptdesc[0].vt
##    1.16: c_int()
##    1.34: c_int(42)
##    2.40: VARIANT()                                   # ctypes.com
##    5.25: variant.value                               # ctypes.com
##   11.20: variant.value = 3.14                        # ctypes.com
##    2.08: VARIANT()                                   # comtypes
##    4.99: variant.value                               # comtypes
##   11.40: variant.value = 3.14                        # comtypes

##ctypes version: 0.9.6
##python version: 2.4.1 (#65, Mar 30 2005, 09:13:57) [MSC v.1310 32 bit (Intel)]
##    0.39: Class()
##    0.99: POINT()
##    1.02: RECT()
##    0.25: point.y
##    2.02: rect.lr
##    6.76: fd.lprgelemdescParam
##    9.43: fd.lprgelemdescParam[0]
##    9.35: fd.lprgelemdescParam[1]
##   11.60: fd.lprgelemdescParam[1].tdesc
##   12.20: fd.lprgelemdescParam[1].tdesc.vt
##   21.40: fd.lprgelemdescParam[1].tdesc.u.lptdesc[0].vt
##    1.19: c_int()
##    1.41: c_int(42)
##    2.24: VARIANT()                                   # ctypes.com
##    5.05: variant.value                               # ctypes.com
##   11.90: variant.value = 3.14                        # ctypes.com
##    1.98: VARIANT()                                   # comtypes
##    4.90: variant.value                               # comtypes
##   11.20: variant.value = 3.14                        # comtypes

# Hm, variant.value did get slower!

##ctypes version: CVS 2005/04/01
##python version: 2.4.1 (#65, Mar 30 2005, 09:13:57) [MSC v.1310 32 bit (Intel)]
##    0.43: Class()
##    0.50: POINT()
##    0.52: RECT()
##    0.28: point.y
##    2.04: rect.lr
##    2.22: fd.lprgelemdescParam
##    4.21: fd.lprgelemdescParam[0]
##    4.18: fd.lprgelemdescParam[1]
##    6.21: fd.lprgelemdescParam[1].tdesc
##    6.43: fd.lprgelemdescParam[1].tdesc.vt
##   12.60: fd.lprgelemdescParam[1].tdesc._.lptdesc[0].vt
##    0.52: c_int()
##    0.74: c_int(42)
##    1.72: VARIANT()                                   # ctypes.com
##    7.81: variant.value                               # ctypes.com
##   10.60: variant.value = 3.14                        # ctypes.com
##    1.51: VARIANT()                                   # comtypes
##    7.86: variant.value                               # comtypes
##   11.70: variant.value = 3.14                        # comtypes

##ctypes version: CVS 2005/04/01 (evening)
##python version: 2.4.1 (#65, Mar 30 2005, 09:13:57) [MSC v.1310 32 bit (Intel)]
##    0.40: Class()                                               
##    0.51: POINT()                                               
##    0.53: RECT()                                                
##    0.27: point.y                                               
##    0.63: rect.lr                                               
##    0.81: fd.lprgelemdescParam                                  
##    1.34: fd.lprgelemdescParam[0]                               
##    1.46: fd.lprgelemdescParam[1]                               
##    2.18: fd.lprgelemdescParam[1].tdesc                         
##    2.45: fd.lprgelemdescParam[1].tdesc.vt                      
##    4.69: fd.lprgelemdescParam[1].tdesc._.lptdesc[0].vt         
##    0.48: c_int()                                               
##    0.70: c_int(42)                                             
##    1.78: VARIANT()                                   # ctypes.c
##    3.36: variant.value                               # ctypes.c
##    8.06: variant.value = 3.14                        # ctypes.c
##    1.55: VARIANT()                                   # comtypes
##    3.31: variant.value                               # comtypes
##    9.30: variant.value = 3.14                        # comtypes

