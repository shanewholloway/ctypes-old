import unittest

from ctypes import *

formats = "bBhHiIlLqQfd"

formats = c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint, \
          c_long, c_ulonglong, c_float, c_double

class ArrayTestCase(unittest.TestCase):
    def test_simple(self):
        # create classes holding simple numeric types, and check
        # various properties.

        init = range(15, 25)

        for fmt in formats:
            alen = len(init)
            class int_array(Array):
                _type_ = fmt
                _length_ = alen

            ia = int_array(*init)
            # length of instance ok?
            self.failUnless(len(ia) == alen)

            # slot values ok?
            values = [ia[i] for i in range(len(init))]
            self.failUnless(values == init)

            # change the items
            from operator import setitem
            new_values = range(42, 42+alen)
            [setitem(ia, n, new_values[n]) for n in range(alen)]
            values = [ia[i] for i in range(len(init))]
            self.failUnless(values == new_values)

            # are the items initialized to 0?
            ia = int_array()
            values = [ia[i] for i in range(len(init))]
            self.failUnless(values == [0] * len(init))

            # Too many in itializers should be caught
            self.assertRaises(IndexError, int_array, *range(alen*2))

        class CharArray(Array):
            _type_ = c_char
            _length_ = 3

        CharArray = c_char * 3

        ca = CharArray("a", "b", "c")

        # Should this work? It doesn't:
        # CharArray("abc")
        self.assertRaises(TypeError, CharArray, "abc")

        self.failUnless(ca[0] == "a")
        self.failUnless(ca[1] == "b")
        self.failUnless(ca[2] == "c")
        self.failUnless(ca[-3] == "a")
        self.failUnless(ca[-2] == "b")
        print ca[-1]
        print len(ca)
##        self.failUnless(ca[-1] == "c")

        # slicing is not supported:
        from operator import getslice, delitem
        self.assertRaises(TypeError, getslice, ca, 0, 1)

        # cannot delete items
        self.assertRaises(TypeError, delitem, ca, 0)

    def _test_numeric_arrays(self):

        alen = 5

        class numarray(Array):
            _type_ = c_int
            _length_ = alen

        na = numarray()
        values = [na[i] for i in range(alen)]
        self.failUnless(values == [0] * alen)

        na = numarray(*[c_int()] * alen)
        values = [na[i] for i in range(alen)]
        self.failUnless(values == [0]*alen)

        na = numarray(1, 2, 3, 4, 5)
        values = [i for i in na]
        self.failUnless(values == [1, 2, 3, 4, 5])

        na = numarray(*map(c_int, (1, 2, 3, 4, 5)))
        values = [i for i in na]
        self.failUnless(values == [1, 2, 3, 4, 5])

def get_suite():
    return unittest.makeSuite(ArrayTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
