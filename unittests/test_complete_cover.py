# -*- coding: latin-1
from ctypes import *
import unittest

class CompleteCoverage(unittest.TestCase):
    def test_cfield(self):
        # tests to make coverage of source/cfield.c more complete

        class X(Structure):
            _fields_ = [("a", c_long),
                        ("b", c_long, 3),
                        ("u", c_wchar),
                        ("U", c_wchar * 3),
                        ("z", c_char_p),
                        ("Z", c_wchar_p),
                        ("P", c_void_p),
                        ("p", POINTER(c_long))]
        self.failUnlessEqual(repr(X.a),
                             "<Field type=c_long, ofs=0, size=4>")
        self.failUnlessEqual(repr(X.b),
                             "<Field type=c_long, ofs=4, bits=3>")
        X().p = None

        # single unicode character
        self.failUnlessRaises(TypeError, lambda: setattr(X(), "u", 42))
        self.failUnlessRaises(TypeError, lambda: setattr(X(), "u", "abc"))
        self.failUnlessRaises(UnicodeDecodeError, lambda: setattr(X(), "u", "ä"))

        # unicode array
        self.failUnlessRaises(TypeError, lambda: setattr(X(), "U", 42))
        X().U = "abc"
        self.failUnlessRaises(UnicodeDecodeError, lambda: setattr(X(), "U", "ä"))

        X().z = 42

        X().Z = 42
        self.failUnlessRaises(TypeError, lambda: setattr(X(), "Z", 3.14))

        x = X()
        x.P = None
        self.failUnlessEqual(x.P, None)
        x.P = 42
        self.failUnlessEqual(x.P, 42)

        self.failUnlessRaises(OverflowError,
                              lambda: setattr(x, "P", 1L << 256))
        self.failUnlessRaises(TypeError,
                              lambda: setattr(x, "P", "abc"))

	pythonapi.PyDict_GetItemString.restype = py_object
	pythonapi.PyDict_GetItemString.argtypes = py_object, c_char_p

	self.failUnlessRaises(ValueError,
                              lambda: pythonapi.PyDict_GetItemString(x.__dict__, "spam"))

if __name__ == "__main__":
    unittest.main()
