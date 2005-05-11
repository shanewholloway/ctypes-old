from ctypes import *
import unittest

class X(Structure):
    _fields_ = [("a", c_int),
                ("b", c_int)]
    def __init__(self):
        self.a = 9
        self.b = 12

class Y(Structure):
    _fields_ = [("x", X)]


class InitTest(unittest.TestCase):
    def test_get(self):
        # make sure the only accessing a nested structure
        # doesn't call the structure's __init__
        y = Y()
        self.failUnlessEqual((y.x.a, y.x.b), (0, 0))

        # But explicitely creating an X structure calls __init__, of course.
        x = X()
        self.failUnlessEqual((x.a, x.b), (9, 12))

        y.x = x
        self.failUnlessEqual((y.x.a, y.x.b), (9, 12))

if __name__ == "__main__":
    unittest.main()
