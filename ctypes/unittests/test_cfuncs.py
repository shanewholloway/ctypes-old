import unittest
from ctypes import *
import _ctypes_test

class CFunctions(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.dll = CDLL(_ctypes_test.__file__)

    def test_byte(self):
        self.dll.tf_b.restype = c_byte
        self.failUnlessEqual(self.dll.tf_b(-42), -42)
        self.dll.tf_bb.restype = c_byte
        self.failUnlessEqual(self.dll.tf_bb(0, -42), -42)

    def test_ubyte(self):
        self.dll.tf_B.restype = c_ubyte
        self.failUnlessEqual(self.dll.tf_B(42), 42)
        self.dll.tf_bB.restype = c_ubyte
        self.failUnlessEqual(self.dll.tf_bB(0, 42), 42)

    def test_short(self):
        self.dll.tf_h.restype = c_short
        self.failUnlessEqual(self.dll.tf_h(-42), -42)
        self.dll.tf_bh.restype = c_short
        self.failUnlessEqual(self.dll.tf_bh(0, -42), -42)

    def test_ushort(self):
        self.dll.tf_H.restype = c_ushort
        self.failUnlessEqual(self.dll.tf_H(42), 42)
        self.dll.tf_bH.restype = c_ushort
        self.failUnlessEqual(self.dll.tf_bH(0, 42), 42)

    def test_int(self):
        self.dll.tf_i.restype = c_int
        self.failUnlessEqual(self.dll.tf_i(-42), -42)
        self.dll.tf_bi.restype = c_int
        self.failUnlessEqual(self.dll.tf_bi(0, -42), -42)

    def test_uint(self):
        self.dll.tf_I.restype = c_uint
        self.failUnlessEqual(self.dll.tf_I(42), 42)
        self.dll.tf_bI.restype = c_uint
        self.failUnlessEqual(self.dll.tf_bI(0, 42), 42)

    def test_long(self):
        self.dll.tf_l.restype = c_long
        self.dll.tf_l.argtypes = (c_long,)
        self.failUnlessEqual(self.dll.tf_l(-42), -42)
        self.dll.tf_bl.restype = c_long
        self.dll.tf_bl.argtypes = (c_byte, c_long)
        self.failUnlessEqual(self.dll.tf_bl(0, -42), -42)

    def test_ulong(self):
        self.dll.tf_L.restype = c_ulong
        self.failUnlessEqual(self.dll.tf_L(42), 42)
        self.dll.tf_bL.restype = c_ulong
        self.failUnlessEqual(self.dll.tf_bL(0, 42), 42)

    def test_longlong(self):
        self.dll.tf_q.restype = c_longlong
        self.dll.tf_q.argtypes = (c_longlong, )
        self.failUnlessEqual(self.dll.tf_q(-42L), -42L)
        self.dll.tf_bq.restype = c_longlong
        self.dll.tf_bq.argtypes = (c_byte, c_longlong)
        self.failUnlessEqual(self.dll.tf_bq(0, -42), -42)

    def test_ulonglong(self):
        self.dll.tf_Q.restype = c_ulonglong
        self.dll.tf_Q.argtypes = (c_longlong, )
        self.failUnlessEqual(self.dll.tf_Q(42), 42)
        self.dll.tf_bQ.restype = c_ulonglong
        self.dll.tf_bQ.argtypes = (c_byte, c_ulonglong)
        self.failUnlessEqual(self.dll.tf_bQ(0, 42), 42)

    def test_float(self):
        self.dll.tf_f.restype = c_float
        self.dll.tf_f.argtypes = (c_float,)
        self.failUnlessEqual(self.dll.tf_f(-42.), -42.)
        self.dll.tf_bf.restype = c_float
        self.dll.tf_bf.argtypes = (c_byte, c_float)
        self.failUnlessEqual(self.dll.tf_bf(0, -42.), -42.)

    def test_double(self):
        self.dll.tf_d.restype = c_double
        self.dll.tf_d.argtypes = (c_double,)
        self.failUnlessEqual(self.dll.tf_d(42), 42)
        self.dll.tf_bd.restype = c_double
        self.dll.tf_bd.argtypes = (c_byte, c_double)
        self.failUnlessEqual(self.dll.tf_bd(0, 42), 42)

    def test_callwithresult(self):
        def process_result(result):
            return result * 2
        self.dll.tf_i.restype = process_result
        self.dll.tf_i.argtypes = (c_int,)
        self.failUnlessEqual(self.dll.tf_i(42), 84)
        self.failUnlessEqual(self.dll.tf_i(-42), -84)

# The following repeates the above tests with stdcall functions (where
# they are available)
try:
    WinDLL
except NameError:
    pass
else:
    class stdcall_dll(WinDLL):
        def __getattr__(self, name):
            if name[:2] == '__' and name[-2:] == '__':
                raise AttributeError, name
            func = self._StdcallFuncPtr("s_" + name, self)
            setattr(self, name, func)
            return func

    class stdcallCFunctions(CFunctions):

        def __init__(self, *args):
            unittest.TestCase.__init__(self, *args)
            self.dll = stdcall_dll(_ctypes_test.__file__)

if __name__ == '__main__':
    unittest.main()
