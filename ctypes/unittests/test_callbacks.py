import unittest
from ctypes import *
import _ctypes_test

class Callbacks(unittest.TestCase):
    functype = CFUNCTYPE

    def callback(self, *args):
        self.got_args = args
        return args[-1]

    def check_type(self, typ, arg):
        PROTO = self.functype.im_func(typ, typ)
        result = PROTO(self.callback)(arg)
        if typ == c_float:
            self.failUnlessAlmostEqual(result, arg, places=5)
        else:
            self.failUnlessEqual(self.got_args, (arg,))
            self.failUnlessEqual(result, arg)

        PROTO = self.functype.im_func(typ, c_byte, typ)
        result = PROTO(self.callback)(-3, arg)
        if typ == c_float:
            self.failUnlessAlmostEqual(result, arg, places=5)
        else:
            self.failUnlessEqual(self.got_args, (-3, arg))
            self.failUnlessEqual(result, arg)

    if not hasattr(unittest.TestCase, "failUnlessAlmostEqual"):
        # This method is not present in Python 2.2
        # Copied from Python 2.3
        def failUnlessAlmostEqual(self, first, second, places=7, msg=None):
            """Fail if the two objects are unequal as determined by their
               difference rounded to the given number of decimal places
               (default 7) and comparing to zero.

               Note that decimal places (from zero) is usually not the same
               as significant digits (measured from the most signficant digit).
            """
            if round(second-first, places) != 0:
                raise self.failureException, \
                      (msg or '%s != %s within %s places' % (`first`, `second`, `places` ))

    ################

    def test_byte(self):
        self.check_type(c_byte, 42)
        self.check_type(c_byte, -42)

    def test_ubyte(self):
        self.check_type(c_ubyte, 42)

    def test_short(self):
        self.check_type(c_short, 42)
        self.check_type(c_short, -42)

    def test_ushort(self):
        self.check_type(c_ushort, 42)

    def test_int(self):
        self.check_type(c_int, 42)
        self.check_type(c_int, -42)

    def test_uint(self):
        self.check_type(c_uint, 42)

    def test_long(self):
        self.check_type(c_long, 42)
        self.check_type(c_long, -42)

    def test_ulong(self):
        self.check_type(c_ulong, 42)

    def test_longlong(self):
        self.check_type(c_longlong, 42)
        self.check_type(c_longlong, -42)

    def test_ulonglong(self):
        self.check_type(c_ulonglong, 42)

    def test_float(self):
        # only almost equal: double -> float -> double
        import math
        self.check_type(c_float, math.e)
        self.check_type(c_float, -math.e)

    def test_double(self):
        self.check_type(c_double, 3.14)
        self.check_type(c_double, -3.14)

    def test_char(self):
        self.check_type(c_char, "x")
        self.check_type(c_char, "a")

    def test_char_p(self):
        self.check_type(c_char_p, "abc")
        self.check_type(c_char_p, "def")

try:
    WINFUNCTYPE
except NameError:
    pass
else:
    class StdcallCallbacks(Callbacks):
        functype = WINFUNCTYPE

################################################################

class SampleCallbacksTestCase(unittest.TestCase):

    def test_integrate(self):
        # Derived from some then non-working code, posted by David Foster
        dll = CDLL(_ctypes_test.__file__)

        # The function prototype called by 'integrate': double func(double);
        CALLBACK = CFUNCTYPE(c_double, c_double)

        # The integrate function itself, exposed from the _ctypes_test dll
        integrate = dll.integrate
        integrate.argtypes = (c_double, c_double, CALLBACK, c_long)
        integrate.restype = c_double

        def func(x):
            return x**2

        result = integrate(0.0, 1.0, CALLBACK(func), 10)
        diff = abs(result - 1./3.)
        
        self.failUnless(diff < 0.01, "%s not less than 0.01" % diff)

################################################################

if __name__ == '__main__':
    unittest.main()
