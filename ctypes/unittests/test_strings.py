import unittest

class StringTestCase(unittest.TestCase):
    pass

##    def test_perf(self):
##        check_perf()
        
from ctypes import c_string

def run_test(rep, msg, func, arg):
    items = range(rep)
    from time import clock
    start = clock()
    for i in items:
        func(arg); func(arg); func(arg); func(arg); func(arg)
    stop = clock()
    print "%20s: %.2f us" % (msg, ((stop-start)*1e6/5/rep))

def check_perf():
    # Construct 5 objects
    from ctypes import c_int

    REP = 200000

    run_test(REP, "c_string(None)", c_string, None)
    run_test(REP, "c_string('abc')", c_string, 'abc')

# Python 2.3 -OO, win2k, P4 700 MHz:
#
#      c_string(None): 1.75 us
#     c_string('abc'): 2.69 us

# Python 2.2 -OO, win2k, P4 700 MHz:
#
#      c_string(None): 2.85 us
#     c_string('abc'): 3.56 us

def get_suite():
    return unittest.makeSuite(StringTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    check_perf()
    unittest.main()
