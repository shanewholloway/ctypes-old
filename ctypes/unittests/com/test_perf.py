# Some preformance measurements

def test(*args):
    from timeit import main
    print args[-1]
    main(args)
    print

from ctypes.com.client import Dispatch
d = Dispatch("InternetExplorer.Application")
fd = d.Navigate.fd

from ctypes import *
class POINT(Structure):
    _fields_ = [("x", c_int), ("y", c_int)]

class RECT(Structure):
    _fields_ = [("ul", POINT), ("lr", POINT)]

class Class(object):
    pass

if __name__ == "__main__":
    # 0.382 us
    test("-s", "from test_perf import Class",
         "Class()")
    # 1.38 us
    test("-s", "from test_perf import POINT",
         "POINT()")
    # 1.43 us
    test("-s", "from test_perf import RECT",
         "RECT()")

    import sys
    sys.exit()

    # 0.238 us
    test("-s", "from test_perf import POINT; pt = POINT()",
         "pt.y")

    # 2.37 us
    test("-s", "from test_perf import RECT; rc = RECT()",
         "rc.lr")

    # 6.72 us
    test("-s", "from test_perf import fd",
         "fd.lprgelemdescParam")

    # 10.4 us = 6.72 us + 3.68 us
    test("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[0]")

    # 10.4 us = 6.72 us + 3.68 us
    test("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1]")

    # 13.2 us = 10.u us + 2.80 us
    test("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1].tdesc")

    # 14 us = 13.2 + 0.8 us
    test("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1].tdesc.vt")

    # 20.7 us = 14 us + 6.7 us
    test("-s", "from test_perf import fd",
         "fd.lprgelemdescParam[1].tdesc.u.lptdesc[0].vt")


    # 1.12 us
    test('-s', "from ctypes import c_int", "c_int()")
    # 1.33 us
    test('-s', "from ctypes import c_int", "c_int(42)")
    # 2.46 us
    test('-s', "from ctypes.com.automation import VARIANT", "VARIANT()")

    # 5.41 us
    test('-s', "from ctypes.com.automation import VARIANT; v = VARIANT(3)", "v.value")

    # 5.27 us
    test('-s', "from comtypes.automation import VARIANT; v = VARIANT(3)", "v.value")

    # 11.7 us
    test('-s', "from ctypes.com.automation import VARIANT; v = VARIANT()", "v.value = 3.14")

    # 13.3 us
    test('-s', "from comtypes.automation import VARIANT; v = VARIANT()", "v.value = 3.14")

