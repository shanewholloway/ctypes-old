import unittest
from ctypes import *

class AnonTest(unittest.TestCase):

    def test_anon(self):
        class ANON(Union):
            _fields_ = [("a", c_int),
                        ("b", c_int)]

        class Y(Structure):
            _fields_ = [("x", c_int),
                        ("_", ANON),
                        ("y", c_int)]
            _anonymous_ = ["_"]

        self.failUnlessEqual(Y.a.offset, sizeof(c_int))
        self.failUnlessEqual(Y.b.offset, sizeof(c_int))

        self.failUnlessEqual(ANON.a.offset, 0)
        self.failUnlessEqual(ANON.b.offset, 0)

    def test_anon_nonseq(self):
        # TypeError: _anonymous_ must be a sequence
        self.failUnlessRaises(TypeError,
                              lambda: type(Structure)("Name",
                                                      (Structure,),
                                                      {"_fields_": [], "_anonymous_": 42}))

    def test_anon_nonmember(self):
        # AttributeError: type object 'Name' has no attribute 'x'
        self.failUnlessRaises(AttributeError,
                              lambda: type(Structure)("Name",
                                                      (Structure,),
                                                      {"_fields_": [],
                                                       "_anonymous_": ["x"]}))

if __name__ == "__main__":
    unittest.main()
