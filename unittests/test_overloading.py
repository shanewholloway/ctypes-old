from ctypes import *
import unittest

class Test(unittest.TestCase):

    def test_from_field(self):

        class TwoTuple(Structure):
            _fields_ = [("i", c_int), ("j", c_int)]

            def __from_field__(cls, ptr):
                assert isinstance(ptr, (int, long))
                # Could we somehow use the CFieldObject descriptors
                # cls.i and cls.j to access the in-memory data block
                # without creating an instance of cls?
                v = cls.from_address(ptr)
                return v.i, v.j
            __from_field__ = classmethod(__from_field__)

            def __to_field__(cls, ptr, value):
                raise "Halt"
                assert isinstance(ptr, (int, long))
                v = cls.from_address(ptr)
                v.i = value[0]
                v.j = value[1]
            __to_field__ = classmethod(__to_field__)

        class X(Structure):
            _fields_ = [("a", TwoTuple)]

        x = X()
        # This works anyway - bad example. __to_field__ is not called.
        x.a = (42, 24)
## EXPERIMENTAL
##        self.failUnlessEqual(x.a, (42, 24))

    def test_sideeffects(self):
        class POINT(Structure):
            _fields_ = [("x", c_int),
                        ("y", c_int)]

        class RECT(Structure):
            _fields_ = [("ul", POINT),
                        ("lr", POINT)]

        # Structures can be initialized by calling them with tuples.
        r = RECT((1, 2), (3, 4))
        self.failUnlessEqual((r.ul.x, r.ul.y), (1, 2))
        self.failUnlessEqual((r.lr.x, r.lr.y), (3, 4))

        # What I didn't even know was that assigning tuples to fields does also work:
        r.ul = (11, 22)
        r.lr = (33, 44)

        self.failUnlessEqual((r.ul.x, r.ul.y), (11, 22))
        self.failUnlessEqual((r.lr.x, r.lr.y), (33, 44))

        # We can also initialize structures with keyword args.
        # Should assigning dicts to fields also work? It doesn't.
        POINT(x=1, y=2)
##        r.ul = {"x":1, "y":2}

if __name__ == "__main__":
    unittest.main()
