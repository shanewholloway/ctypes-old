import unittest
from ctypes import *

class Callbacks(unittest.TestCase):
    functype = CFUNCTYPE

    def callback(self, *args):
        self.got_args = args
        return args[-1]

    def check_type(self, typ, arg):
        PROTO = self.functype.im_func(typ, typ)
        return PROTO(self.callback)(arg)

    def check_type_1(self, typ, arg):
        PROTO = self.functype.im_func(typ, c_byte, typ)
        return PROTO(self.callback)(-3, arg)

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
        self.failUnlessEqual(self.check_type(c_byte, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_byte, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_ubyte(self):
        self.failUnlessEqual(self.check_type(c_ubyte, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_ubyte, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_short(self):
        self.failUnlessEqual(self.check_type(c_short, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_short, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_ushort(self):
        self.failUnlessEqual(self.check_type(c_ushort, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_ushort, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_int(self):
        self.failUnlessEqual(self.check_type(c_int, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_int, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_uint(self):
        self.failUnlessEqual(self.check_type(c_uint, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_uint, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_long(self):
        self.failUnlessEqual(self.check_type(c_long, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_long, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_ulong(self):
        self.failUnlessEqual(self.check_type(c_ulong, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_ulong, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_longlong(self):
        self.failUnlessEqual(self.check_type(c_longlong, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_longlong, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_ulonglong(self):
        self.failUnlessEqual(self.check_type(c_ulonglong, 42), 42)
        self.failUnlessEqual(self.got_args, (42,))
        self.failUnlessEqual(self.check_type_1(c_ulonglong, 42), 42)
        self.failUnlessEqual(self.got_args, (-3, 42))

    def test_float(self):
        # only almost equal: double -> float -> double
        import math
        self.failUnlessAlmostEqual(self.check_type(c_float, math.e), math.e,
                                   places=6)
        self.failUnlessAlmostEqual(self.got_args[0], math.e, places=6)
        self.failUnlessAlmostEqual(self.check_type_1(c_float, math.e), math.e,
                                   places=6)
        self.failUnlessAlmostEqual(self.got_args[1], math.e, places=6)

    def test_double(self):
        self.failUnlessEqual(self.check_type(c_double, 3.14), 3.14)
        self.failUnlessEqual(self.got_args, (3.14,))
        self.failUnlessEqual(self.check_type_1(c_double, 3.14), 3.14)
        self.failUnlessEqual(self.got_args, (-3, 3.14))

    def test_char(self):
        self.failUnlessEqual(self.check_type(c_char, "x"), "x")
        self.failUnlessEqual(self.got_args, ("x",))
        self.failUnlessEqual(self.check_type_1(c_char, "x"), "x")
        self.failUnlessEqual(self.got_args, (-3, "x"))

    def test_char_p(self):
        self.failUnlessEqual(self.check_type(c_char_p, "abc"), "abc")
        self.failUnlessEqual(self.got_args, ("abc",))
        self.failUnlessEqual(self.check_type_1(c_char_p, "abc"), "abc")
        self.failUnlessEqual(self.got_args, (-3, "abc"))

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
        
        self.failUnless(diff < 0.01, "%s not less than 0.01" % diff)

################################################################

if __name__ == '__main__':
    unittest.main()
