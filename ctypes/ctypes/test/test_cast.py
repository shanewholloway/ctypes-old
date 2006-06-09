from ctypes import *
import unittest
import sys

class Test(unittest.TestCase):

    def test_array2pointer(self):
        array = (c_int * 3)(42, 17, 2)

        # casting an array to a pointer works.
        ptr = cast(array, POINTER(c_int))
        self.failUnlessEqual([ptr[i] for i in range(3)], [42, 17, 2])

        if 2*sizeof(c_short) == sizeof(c_int):
            ptr = cast(array, POINTER(c_short))
            if sys.byteorder == "little":
                self.failUnlessEqual([ptr[i] for i in range(6)],
                                     [42, 0, 17, 0, 2, 0])
            else:
                self.failUnlessEqual([ptr[i] for i in range(6)],
                                     [0, 42, 0, 17, 0, 2])

    def test_address2pointer(self):
        array = (c_int * 3)(42, 17, 2)

        address = addressof(array)
        ptr = cast(c_void_p(address), POINTER(c_int))
        self.failUnlessEqual([ptr[i] for i in range(3)], [42, 17, 2])

        ptr = cast(address, POINTER(c_int))
        self.failUnlessEqual([ptr[i] for i in range(3)], [42, 17, 2])

    def test_p2a_objects(self):
        array = (c_char_p * 5)()
        self.failUnlessEqual(array._objects, None)
        array[0] = "foo bar"
        self.failUnlessEqual(array._objects, {'0': "foo bar"})

        p = cast(array, POINTER(c_char_p))
        # array and p share a common _objects attribute
        self.failUnless(p._objects is array._objects)
        self.failUnlessEqual(array._objects, {'0': "foo bar"})
        p[0] = "spam spam"
        self.failUnlessEqual(p._objects, {'0': "spam spam"})
        self.failUnlessEqual(array._objects, {'0': "spam spam"})
        p[1] = "foo bar"
        self.failUnlessEqual(p._objects, {'1': 'foo bar', '0': "spam spam"})
        self.failUnlessEqual(array._objects, {'1': 'foo bar', '0': "spam spam"})


if __name__ == "__main__":
    unittest.main()
