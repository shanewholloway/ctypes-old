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

class ReturnFuncPtrTestCase(unittest.TestCase):

    def test_with_prototype(self):
        # The _ctypes_test shared lib/dll exports quite some functions for testing.
        # The get_strchr function returns a *pointer* to the C strchr function.
        dll = CDLL(find_test_dll())
        get_strchr = dll.get_strchr
        get_strchr.restype = CFUNCTYPE(c_char_p, c_char_p, c_char)
        strchr = get_strchr()
        self.failUnlessEqual(strchr("abcdef", "b"), "bcdef")
        self.failUnlessEqual(strchr("abcdef", "x"), None)
        self.assertRaises(ArgumentError, strchr, "abcdef", 3)
        self.assertRaises(TypeError, strchr, "abcdef")
        
    def test_without_prototype(self):
        dll = CDLL(find_test_dll())
        get_strchr = dll.get_strchr
        addr = get_strchr()
        # _CFuncPtr instances are now callable with an integer argument
        # which denotes a function address:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(addr)
        self.failUnless(strchr("abcdef", "b"), "bcdef")
        self.failUnlessEqual(strchr("abcdef", "x"), None)
        self.assertRaises(ArgumentError, strchr, "abcdef", 3)
        self.assertRaises(TypeError, strchr, "abcdef")

if __name__ == "__main__":
    unittest.main()
