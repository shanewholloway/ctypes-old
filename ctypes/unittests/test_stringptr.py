import unittest
from ctypes import *

class X(Structure):
    _fields_ = [("str", POINTER(c_char))]

class X2(Structure):
    _fields_ = [("str", c_char_p)]

class StringPtrTestCase(unittest.TestCase):
    def test_X(self):
        x = X()

        # NULL pointer access
        self.assertRaises(ValueError, getattr, x.str, "contents")
        b = c_buffer("Hello, World")
        from sys import getrefcount as grc
        self.failUnlessEqual(grc(b), 2)
        x.str = b
        self.failUnlessEqual(grc(b), 3)
        for i in range(len(b)):
            self.failUnlessEqual(b[i], x.str[i])

        self.assertRaises(TypeError, setattr, x, "str", "Hello, World")

    def test_X2(self):
        x = X2()

        self.failUnlessEqual(x.str, None)
        x.str = "Hello, World"
        self.failUnlessEqual(x.str, "Hello, World")
        b = c_buffer("Hello, World")
        self.failUnlessRaises(TypeError, setattr, x, "str", b)



def get_suite():
    return unittest.makeSuite(StringPtrTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    test()
