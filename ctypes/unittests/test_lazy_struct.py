import unittest
from ctypes import *

class LazyStructTest(unittest.TestCase):
    def test(self):
        class POINT(Structure):
            pass
        POINT._fields_ = [("x", c_int), ("y", c_int)]

        p = POINT(1, 2)
        self.failUnlessEqual((p.x, p.y), (1, 2))

    def test_pointers(self):
        class List(Structure):
            pass
        List._fields_ = [("num", c_int), ("pnext", POINTER(List))]

        a = List(1)
        b = List(2)

        self.failUnlessEqual(bool(a.pnext), False)
        self.failUnlessEqual(bool(b.pnext), False)

        a.pnext = pointer(b)
        b.pnext = pointer(a)

        self.failUnlessEqual(a.num, 1)
        self.failUnlessEqual(a.pnext[0].num, 2)
        self.failUnlessEqual(a.pnext[0].pnext[0].num, 1)

    def test_reassign(self):
        class List(Structure):
            pass
        List._fields_ = [("num", c_int), ("pnext", POINTER(List))]

        self.assertRaises(AttributeError,
                          setattr, List, "_fields_",
                          [("num", c_int)])

    def test_subclasses(self):
        class Point(Structure):
            _fields_ = [("x", c_int), ("y", c_int)]

        class ColoredPoint(Point):
            _fields_ = Point._fields_ + [("color", c_int)]
        self.failUnlessEqual(sizeof(ColoredPoint), sizeof(c_int) * 3)

        # This has to wait - it currently fails with:
        # _fields_ cannot be overwritten.
##        class HeavyPoint(Point):
##            pass
##        HeavyPoint._fields_ = Point._fields_ + [("weight", c_int)]
##        self.failUnlessEqual(sizeof(HeavyPoint), sizeof(c_int) * 3)
        
if __name__ == "__main__":
    unittest.main()
