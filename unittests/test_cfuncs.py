import unittest
from ctypes import *
import _ctypes_test

dll = CDLL(_ctypes_test.__file__)

class CFunctions(unittest.TestCase):
    def test_short(self):
        dll.tf_h.restype = c_short
        self.failUnlessEqual(dll.tf_h(-42), -42)
        dll.tf_bh.restype = c_short
        self.failUnlessEqual(dll.tf_bh(0, -42), -42)

    def test_ushort(self):
        dll.tf_H.restype = c_ushort
        self.failUnlessEqual(dll.tf_H(42), 42)
        dll.tf_bH.restype = c_ushort
        self.failUnlessEqual(dll.tf_bH(0, 42), 42)

    def test_int(self):
        dll.tf_i.restype = c_int
        self.failUnlessEqual(dll.tf_i(-42), -42)
        dll.tf_bi.restype = c_int
        self.failUnlessEqual(dll.tf_bi(0, -42), -42)

    def test_uint(self):
        dll.tf_I.restype = c_uint
        self.failUnlessEqual(dll.tf_I(42), 42)
        dll.tf_bI.restype = c_uint
        self.failUnlessEqual(dll.tf_bI(0, 42), 42)

    def test_long(self):
        dll.tf_l.restype = c_long
        self.failUnlessEqual(dll.tf_l(-42), -42)
        dll.tf_bl.restype = c_long
        self.failUnlessEqual(dll.tf_bl(0, -42), -42)

    def test_ulong(self):
        dll.tf_L.restype = c_ulong
        self.failUnlessEqual(dll.tf_L(42), 42)
        dll.tf_bL.restype = c_ulong
        self.failUnlessEqual(dll.tf_bL(0, 42), 42)

if __name__ == '__main__':
    unittest.main()
