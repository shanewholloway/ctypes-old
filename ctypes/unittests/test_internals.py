# This tests the internal _objects attribute
import unittest
from ctypes import *
from sys import getrefcount as grc

"""
ctypes' types are container types.

They have an internal memory block, which only consists of some bytes,
but it has to keep references to other objects as well. This is not
really needed for trivial C types like int or char, but it is important
for aggregate types like strings or pointers in particular.

What about pointers?

"""

class ObjectsTestCase(unittest.TestCase):
    def failUnlessSame(self, a, b):
        self.failUnlessEqual(id(a), id(b))

    def test_ints(self):
        i = 42000123
        self.failUnlessEqual(3, grc(i))
        ci = c_int(i)
        self.failUnlessEqual(4, grc(i))
        self.failUnlessSame(i, ci._objects[0])
        self.failUnlessEqual([i], ci._objects)

    def test_c_char_p(self):
        s = "Hello, World"
        self.failUnlessEqual(3, grc(s))
        cs = c_char_p(s)
        self.failUnlessEqual(4, grc(s))
        self.failUnlessSame(s, cs._objects[0])
        self.failUnlessEqual([s], cs._objects)

    def test_simple_struct(self):
        class X(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]

        a = 421234
        b = 421235
        x = X()
        self.failUnlessEqual(x._objects, [None, None])
        x.a = a
        x.b = b
        self.failUnlessEqual(x._objects, [a, b])
        self.failUnlessSame(x._objects[0], a)

    def test_embedded_structs(self):
        class X(Structure):
            _fields_ = [("a", c_int), ("b", c_int)]

        class Y(Structure):
            _fields_ = [("x", X), ("y", X)]

        y = Y()
        self.failUnlessEqual(y._objects, [None, None])

        x1, x2 = X(), X()
        y.x, y.y = x1, x2
        self.failUnlessEqual(y._objects, [[None, None], [None, None]])
        x1.a, x2.b = 42, 93
        self.failUnlessEqual(y._objects, [[42, None], [None, 93]])
##        self.failUnlessEqual(y.x._objects, [42, None])

    def test_xxx(self):
        class X(Structure):
            _fields_ = [("a", c_char_p), ("b", c_char_p)]

        class Y(Structure):
            _fields_ = [("x", X), ("y", X)]

        s1 = "Hello, World"
        s2 = "Hallo, Welt"

        x = X()
        x.a = s1
        x.b = s2
        self.failUnlessEqual(x._objects, [s1, s2])

        y = Y()
        y.x = x
        self.failUnlessEqual(y._objects, [[s1, s2], None])
##        x = y.x
##        del y
##        print x._b_base_._objects

    def test_ptr_struct(self):
        class X(Structure):
            _fields_ = [("data", POINTER(c_int))]

        A = c_int*4
        a = A(11, 22, 33, 44)
        self.failUnlessEqual(a._objects, [11, 22, 33, 44])

        x = X()
        x.data = a
##XXX        print x._objects
##XXX        print x.data[0]
##XXX        print x.data._objects

def get_suite():
    return unittest.makeSuite(ObjectsTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    test()
