import unittest
from ctypes import *

class CallbacksTestCase(unittest.TestCase):

    def test_cdecl_callback(self):
        import _ctypes_test
        CALLBACK = CFUNCTYPE(c_int, c_int, c_int)
        e_func = CDLL(_ctypes_test.__file__)._testfunc_callback_i_iif

        def func(a, b):
##            print "cdecl func called with", a, b
            return a + b

        result = e_func(10, CALLBACK(func))
        self.failUnlessEqual(result, 54)

    def test_stdcall_callback(self):
        import _ctypes_test
        try:
            WINFUNCTYPE
        except NameError:
            WINFUNCTYPE = CFUNCTYPE
        CALLBACK = WINFUNCTYPE(c_int, c_int, c_int)
        e_func = CDLL(_ctypes_test.__file__)._testfunc_stdcall_callback_i_iif

        def func(a, b):
##            print "stdcall func called with", a, b
            return a + b

        result = e_func(10, CALLBACK(func))
        self.failUnlessEqual(result, 54)

    def test_simple_callback(self):
        import _ctypes_test
        CALLBACK = CFUNCTYPE(c_int, c_int)
        e_func = CDLL(_ctypes_test.__file__)._testfunc_callback_i_if

        def func(x):
##            print "func called with", x
            return x

        result = e_func(10, CALLBACK(func))
        self.failUnlessEqual(result, 18)

    def test_integrate(self):
        # Derived from some then non-working code, posted by David Foster
        import _ctypes_test

        # The function prototype called by 'integrate': double func(double);
        CALLBACK = CFUNCTYPE(c_double, c_double)

        # The integrate function itself, exposed from the _ctypes_test dll
        integrate = CDLL(_ctypes_test.__file__).integrate
        integrate.argtypes = (c_double, c_double, CALLBACK, c_long)
        integrate.restype = c_double

        import sys

        def func(x):
            print >> sys.stderr, "func got", x
            return x**2

        result = integrate(0.0, 1.0, CALLBACK(func), 10)
        diff = abs(result - 1./3.)
        
        self.failUnless(diff < 0.01, "%s not less than 0.01" % diff)
                                   
        

def get_suite():
    return unittest.makeSuite(CallbacksTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
