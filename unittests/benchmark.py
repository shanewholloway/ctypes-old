import sys
from ctypes import cdll, c_int, c_char_p
import _ctypes_test

ex_func_si = cdll[_ctypes_test.__file__]._py_func_si
##ex_func_si.argtypes = c_char_p, c_int
##ex_func_si.restype = None
py_func_si = _ctypes_test.func_si

ex_func = cdll[_ctypes_test.__file__]._py_func
##ex_func.argtypes = ()
##ex_func.restype = None
py_func = _ctypes_test.func

REPEAT = int(1e6)

if __name__ == "__main__":
    from timeit import Timer

    t = Timer("ex_func_si('abc', 3)", "from __main__ import ex_func_si")
    # win32: 1.20 us
    # suse9.1 (vmware): 2.314 us
    t1 = t.timeit(REPEAT) *1e6 / REPEAT
    print >> sys.stderr, "dll call, 2 args:  %.2f us" % t1
    t = Timer("py_func_si('abc', 3)", "from __main__ import py_func_si")
    # win32: 0.65 us
    # suse9.1(vmware): 0.910 us
    t2 = t.timeit(REPEAT) *1e6 / REPEAT
    print >> sys.stderr, "func call, 2 args: %.2f us" % t2
    # win32: ratio 1.9
    print >> sys.stderr, "ratio %.1f" % (t1 / t2)
    print >> sys.stderr

    t = Timer("ex_func()", "from __main__ import ex_func")
    # win32: 0.82 us
    # suse9.1(vmware): 1.521 us
    t1 = t.timeit(REPEAT) *1e6 / REPEAT
    print >> sys.stderr, "dll call, no args:  %.2f us" % t1
    t = Timer("py_func()", "from __main__ import py_func")
    # win32: 0.14 us
    # suse9.1(vmware): 0.231 us
    t2 = t.timeit(REPEAT) *1e6 / REPEAT
    print >> sys.stderr, "func call, no args: %.2f us" % t2
    # win32: ratio 5.8
    print >> sys.stderr, "ratio %.1f" % (t1 / t2)
    print >> sys.stderr
