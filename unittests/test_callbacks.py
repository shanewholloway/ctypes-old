import unittest
from ctypes import *

class CallbacksTestCase(unittest.TestCase):

    def test_integrate(self):
        # Derived from some then non-working code, posted by David Foster
        import _ctypes_test

        # The function prototype called by 'integrate': double func(double);
        CALLBACK = CFUNCTYPE(c_double, c_double)

        # The integrate function itself, exposed from the _ctypes_test dll
        integrate = CDLL(_ctypes_test.__file__).integrate
        integrate.argtypes = (c_double, c_double, CALLBACK, c_long)
        integrate.restype = c_double

        def func(x):
            return x**2

        result = integrate(0.0, 1.0, CALLBACK(func), 10)
        diff = abs(result - 1./3.)
        
        self.failUnless(diff < 0.01)
                                   
        

def get_suite():
    return unittest.makeSuite(CallbacksTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
