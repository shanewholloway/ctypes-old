# -*- coding: latin-1 -*-
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
##        self.failUnlessRaises(UnicodeDecodeError, lambda: setattr(X(), "u", "�"))

        # unicode array
        self.failUnlessRaises(TypeError, lambda: setattr(X(), "U", 42))
        X().U = "abc"
##        self.failUnlessRaises(UnicodeDecodeError, lambda: setattr(X(), "U", "�"))

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

    def test__ctypes(self):
        # only int allowed
        self.assertRaises(TypeError, lambda: c_int.from_address("xyz"))

        # "Os"
        self.assertRaises(TypeError, lambda: c_int.in_dll(object(), 42))
        self.assertRaises(AttributeError, lambda: c_int.in_dll(object(), "x"))

        class Fake(object):
            _handle = "abc"

        # dll must have an 'integer' _handle atrrib
        self.assertRaises(TypeError, lambda: c_int.in_dll(Fake(), "x"))

        # setting normal attributes on Structures/Unions
        class X(Structure):
            _fields_ = [("a", c_int)]
        class Y(Union):
            _fields_ = [("a", c_int)]
        X.b = 99
        Y.b = 99
        self.failUnlessRaises(TypeError, lambda: setattr(X, "__dict__", {})) # unwriteable
        self.failUnlessRaises(TypeError, lambda: setattr(Y, "__dict__", {})) # unwriteable

        # from_param
        print c_int.from_param(c_int(42))

    def test_pointer(self):
        class POINT(Structure):
            _fields_ = [("x", c_int),
                        ("y", c_int)]

        class PP(Structure):
            _fields_ = [("pt1", POINTER(POINT))]

        pp = PP()

        # THIS ONE CRASHES WITH an object having negative refcount:
        # The bug was already in 0.9.6 at least
#XXX        pp.pt1 = cast(42, POINTER(POINT))

##        pp.pt1 = pointer(POINT(1, 2))
##        pp.pt1[0].x
##        pp.pt1[0].y


if __name__ == "__main__":
    unittest.main()