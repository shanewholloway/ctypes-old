import unittest
from ctypes import *

def find_test_dll():
    import sys, os
    if os.name == "nt":
        name = "_ctypes_test.pyd"
    else:
        name = "_ctypes_test.so"
    for p in sys.path:
        f = os.path.join(p, name)
        if os.path.isfile(f):
            return f

class SlicesTestCase(unittest.TestCase):
    def test_getslice_cint(self):
        a = (c_int * 100)(*xrange(1100, 1200))
        b = range(1100, 1200)
        self.failUnlessEqual(a[0:2], b[0:2])
        self.failUnlessEqual(len(a), len(b))
        self.failUnlessEqual(a[5:7], b[5:7])
        self.failUnlessEqual(a[-1], b[-1])
        self.failUnlessEqual(a[:], b[:])

        a[0:5] = range(5, 10)
        self.failUnlessEqual(a[0:5], range(5, 10))

    def test_setslice_cint(self):
        a = (c_int * 100)(*xrange(1100, 1200))
        b = range(1100, 1200)

        a[32:47] = range(32, 47)
        self.failUnlessEqual(a[32:47], range(32, 47))

        from operator import setslice

        # TypeError: int expected instead of str instance
        self.assertRaises(TypeError, setslice, a, 0, 5, "abcde")
        # TypeError: int expected instead of str instance
        self.assertRaises(TypeError, setslice, a, 0, 5, ["a", "b", "c", "d", "e"])
        # TypeError: int expected instead of float instance
        self.assertRaises(TypeError, setslice, a, 0, 5, [1, 2, 3, 4, 3.14])
        # ValueError: Can only assign sequence of same size
        self.assertRaises(ValueError, setslice, a, 0, 5, range(32))

    def test_char_ptr(self):
        s = "abcdefghijklmnopqrstuvwxyz\0"

        dll = CDLL(find_test_dll())
        dll.my_strdup.restype = POINTER(c_char)
        res = dll.my_strdup(s)
        self.failUnlessEqual(res[:len(s)], s)

        import operator
        self.assertRaises(TypeError, operator.setslice,
                          res, 0, 5, u"abcde")

        dll.my_strdup.restype = POINTER(c_byte)
        res = dll.my_strdup(s)
        self.failUnlessEqual(res[:len(s)-1], range(ord("a"), ord("z")+1))

    def test_char_array(self):
        s = "abcdefghijklmnopqrstuvwxyz\0"

        p = (c_char * 27)(*s)
        self.failUnlessEqual(p[:], s)


    try:
        c_wchar
    except NameError:
        pass
    else:
        def test_wchar_ptr(self):
            s = u"abcdefghijklmnopqrstuvwxyz\0"

            dll = CDLL(find_test_dll())
            dll.my_wcsdup.restype = POINTER(c_wchar)
            res = dll.my_wcsdup(s)
            self.failUnlessEqual(res[:len(s)], s)

            import operator
            self.assertRaises(TypeError, operator.setslice,
                              res, 0, 5, u"abcde")

            dll.my_wcsdup.restype = POINTER(c_short)
            res = dll.my_wcsdup(s)
            self.failUnlessEqual(res[:len(s)-1], range(ord("a"), ord("z")+1))

################################################################

if __name__ == "__main__":
    unittest.main()
