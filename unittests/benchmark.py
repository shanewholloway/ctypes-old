import sys
from ctypes import cdll
import _ctypes_test

ex_func_si = cdll[_ctypes_test.__file__]._py_func_si
py_func_si = _ctypes_test.func_si

ex_func = cdll[_ctypes_test.__file__]._py_func
py_func = _ctypes_test.func

if __name__ == "__main__":
    from timeit import Timer

    t = Timer("ex_func_si('abc', 3)", "from __main__ import ex_func_si")
    # win32: 1.284 us
    # suse9.1 (vmware): 2.314 us
    print >> sys.stderr, "dll call, 2 args:  %.3f us" % t.timeit()
    t = Timer("py_func_si('abc', 3)", "from __main__ import py_func_si")
    # win32: 0.629 us
    # suse9.1(vmware): 0.910 us
    print >> sys.stderr, "func call, 2 args: %.3f us" % t.timeit()
    print >> sys.stderr

    t = Timer("ex_func()", "from __main__ import ex_func")
    # win32: 0.773 us
    # suse9.1(vmware): 1.521 us
    print >> sys.stderr, "dll call, no args:  %.3f us" % (t.timeit(10000000) / 10)
    t = Timer("py_func()", "from __main__ import py_func")
    # win32: 0.139 us
    # suse9.1(vmware): 0.231 us
    print >> sys.stderr, "func call, no args: %.3f us" % (t.timeit(10000000) / 10)
    print >> sys.stderr
