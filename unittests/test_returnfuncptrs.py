import unittest
from ctypes import *
import _ctypes

class ReturnFuncPtrTestCase(unittest.TestCase):

    def test_with_prototype(self):
        dll = CDLL(_ctypes.__file__)
        # The _ctypes shared lib/dll exports quite some functions for testing.
        # The get_strchr function returns a *pointer* to the C strchr function.
        get_strchr = dll.get_strchr
        get_strchr.restype = CFUNCTYPE(c_char_p, c_char_p, c_char)
        strchr = get_strchr()
        self.failUnlessEqual(strchr("abcdef", "b"), "bcdef")
        self.failUnlessEqual(strchr("abcdef", "x"), None)
        self.assertRaises(TypeError, strchr, "abcdef", 3)
        self.assertRaises(TypeError, strchr, "abcdef")
        
    def test__without_prototype(self):
        dll = CDLL(_ctypes.__file__)
        get_strchr = dll.get_strchr
        addr = get_strchr()
        # _CFuncPtr instances are now callable with an integer argument
        # which denotes a function address:
        strchr = CFUNCTYPE(c_char_p, c_char_p, c_char)(addr)
        self.failUnless(strchr("abcdef", "b"), "bcdef")
        self.failUnlessEqual(strchr("abcdef", "x"), None)
        self.assertRaises(TypeError, strchr, "abcdef", 3)
        self.assertRaises(TypeError, strchr, "abcdef")

def get_suite():
    return unittest.makeSuite(ReturnFuncPtrTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == "__main__":
    unittest.main()
