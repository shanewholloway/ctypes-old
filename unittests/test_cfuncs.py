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

    def test_longlong(self):
        dll.tf_q.restype = c_longlong
        dll.tf_q.argtypes = (c_longlong, )
        self.failUnlessEqual(dll.tf_q(-42L), -42L)
        dll.tf_bq.restype = c_longlong
        dll.tf_bq.argtypes = (c_byte, c_longlong)
        self.failUnlessEqual(dll.tf_bq(0, -42), -42)

    def test_ulonglong(self):
        dll.tf_Q.restype = c_ulonglong
        dll.tf_Q.argtypes = (c_longlong, )
        self.failUnlessEqual(dll.tf_Q(42), 42)
        dll.tf_bQ.restype = c_ulonglong
        dll.tf_bQ.argtypes = (c_byte, c_ulonglong)
        self.failUnlessEqual(dll.tf_bQ(0, 42), 42)

    def test_float(self):
        dll.tf_f.restype = c_float
        dll.tf_f.argtypes = (c_float,)
        self.failUnlessEqual(dll.tf_f(-42.), -42.)
        dll.tf_bf.restype = c_float
        dll.tf_bf.argtypes = (c_byte, c_float)
        self.failUnlessEqual(dll.tf_bf(0, -42.), -42.)

    def test_double(self):
        dll.tf_d.restype = c_double
        dll.tf_d.argtypes = (c_double,)
        self.failUnlessEqual(dll.tf_d(42), 42)
        dll.tf_bd.restype = c_double
        dll.tf_bd.argtypes = (c_byte, c_double)
        self.failUnlessEqual(dll.tf_bd(0, 42), 42)

if __name__ == '__main__':
    unittest.main()
