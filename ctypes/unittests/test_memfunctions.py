import unittest
from ctypes import *

class MemFunctionsTest(unittest.TestCase):
    def test_memmove(self):
        a = create_string_buffer(32)
        p = "Hello, World"
        result = memmove(a, p, len(p))
        self.failUnlessEqual(a.value, "Hello, World")

        self.failUnlessEqual(get_string(result), "Hello, World")

if __name__ == "__main__":
    unittest.main()
