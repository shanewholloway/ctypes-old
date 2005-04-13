from ctypes import *
import unittest

nums = [c_byte, c_short, c_int, c_long, c_longlong,
        c_ubyte, c_ushort, c_uint, c_ulong, c_ulonglong,
        c_float, c_double]

class ReprTest(unittest.TestCase):
    def test_numbers(self):
        for typ in nums:
            self.failUnless(repr(typ(42)).startswith(typ.__name__))
            class X(typ):
                pass
            self.failUnlessEqual("X(42", repr(X(42))[:4])

    def test_char(self):
        self.failUnlessEqual("c_char('x')", repr(c_char('x')))

        class X(c_char):
            pass
        self.failUnlessEqual("X('x')", repr(X('x')))

if __name__ == "__main__":
    unittest.main()
