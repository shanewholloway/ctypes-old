from ctypes import *
import unittest

def get_libc():
    import os, sys
    if os.name == "nt":
        return cdll.msvcrt
    else:
        return cdll.libc
libc = get_libc()

class LibTest(unittest.TestCase):
    def test_strcpy(self):
        comparefunc = CFUNCTYPE(c_int, POINTER(c_char), POINTER(c_char))
        libc.qsort.argtypes = c_void_p, c_int, c_int, comparefunc
        libc.qsort.restype = None

        def sort(a, b):
            return cmp(a[0], b[0])

        chars = create_string_buffer("spam, spam, and spam")
        libc.qsort(chars, len(chars)-1, sizeof(c_char), comparefunc(sort))
        print repr(chars.raw)

if __name__ == "__main__":
    unittest.main()
