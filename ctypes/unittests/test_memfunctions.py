import unittest
from ctypes import *

class MemFunctionsTest(unittest.TestCase):
    def test_memmove(self):
        a = create_string_buffer(32)
        p = "Hello, World"
        result = memmove(a, p, len(p))
        self.failUnlessEqual(a.value, "Hello, World")

        self.failUnlessEqual(get_string(result), "Hello, World")
        self.failUnlessEqual(get_string(result, 5), "Hello")
        self.failUnlessEqual(get_string(result, 16), "Hello, World\0\0\0\0")

    def test_memset(self):
        a = create_string_buffer(32)
        result = memset(a, ord('x'), 16)

        self.failUnlessEqual(get_string(result), "xxxxxxxxxxxxxxxx")
        self.failUnlessEqual(get_string(a), "xxxxxxxxxxxxxxxx")
        self.failUnlessEqual(a.value, "xxxxxxxxxxxxxxxx")

if __name__ == "__main__":
    unittest.main()
