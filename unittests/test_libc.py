from ctypes import *
import unittest

libc = cdll.find('c', False)
libm = cdll.find('m', False)

class LibTest(unittest.TestCase):
    def test_sqrt(self):
        libm.sqrt.argtypes = c_double,
        libm.sqrt.restype = c_double
        self.failUnlessEqual(libm.sqrt(4.0), 2.0)
        import math
        self.failUnlessEqual(libm.sqrt(2.0), math.sqrt(2.0))
        

    def test_qsort(self):
        comparefunc = CFUNCTYPE(c_int, POINTER(c_char), POINTER(c_char))
        libc.qsort.argtypes = c_void_p, c_int, c_int, comparefunc
        libc.qsort.restype = None

        def sort(a, b):
            return cmp(a[0], b[0])

        chars = create_string_buffer("spam, spam, and spam")
        libc.qsort(chars, len(chars)-1, sizeof(c_char), comparefunc(sort))
        self.failUnlessEqual(chars.raw, "   ,,aaaadmmmnpppsss\x00")

if __name__ == "__main__":
    unittest.main()
