# A lot of failures in these tests on Mac OS X.
# Byte order related?

import unittest
from ctypes import *

# These two functions report the argument in the last call to one of
# the tf_? functions.

import _ctypes_test
testdll = CDLL(_ctypes_test.__file__)

def S():
    return c_longlong.in_dll(testdll, "last_tf_arg_s").value
def U():
    return c_ulonglong.in_dll(testdll, "last_tf_arg_u").value

class CFunctions(unittest.TestCase):

    def test_byte(self):
        testdll.tf_b.restype = c_byte
        testdll.tf_b.argtypes = (c_byte,)
        self.failUnlessEqual(testdll.tf_b(-126), -42)
        self.failUnlessEqual(S(), -126)

    def test_byte_plus(self):
        testdll.tf_bb.restype = c_byte
        testdll.tf_bb.argtypes = (c_byte, c_byte)
        self.failUnlessEqual(testdll.tf_bb(0, -126), -42)
        self.failUnlessEqual(S(), -126)

    def test_ubyte(self):
        testdll.tf_B.restype = c_ubyte
        testdll.tf_B.argtypes = (c_ubyte,)
        self.failUnlessEqual(testdll.tf_B(255), 85)
        self.failUnlessEqual(U(), 255)

    def test_ubyte_plus(self):
        testdll.tf_bB.restype = c_ubyte
        testdll.tf_bB.argtypes = (c_byte, c_ubyte)
        self.failUnlessEqual(testdll.tf_bB(0, 255), 85)
        self.failUnlessEqual(U(), 255)

    def test_short(self):
        testdll.tf_h.restype = c_short
        self.failUnlessEqual(testdll.tf_h(-32766), -10922)
        self.failUnlessEqual(S(), -32766)

    def test_short_plus(self):
        testdll.tf_bh.restype = c_short
        self.failUnlessEqual(testdll.tf_bh(0, -32766), -10922)
        self.failUnlessEqual(S(), -32766)

    def test_ushort(self):
        testdll.tf_H.restype = c_ushort
        self.failUnlessEqual(testdll.tf_H(65535), 21845)
        self.failUnlessEqual(U(), 65535)

    def test_ushort_plus(self):
        testdll.tf_bH.restype = c_ushort
        self.failUnlessEqual(testdll.tf_bH(0, 65535), 21845)
        self.failUnlessEqual(U(), 65535)

    def test_int(self):
        testdll.tf_i.restype = c_int
        self.failUnlessEqual(testdll.tf_i(-2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)

    def test_int_plus(self):
        testdll.tf_bi.restype = c_int
        self.failUnlessEqual(testdll.tf_bi(0, -2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)

    def test_uint(self):
        testdll.tf_I.restype = c_uint
        self.failUnlessEqual(testdll.tf_I(4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)

    def test_uint_plus(self):
        testdll.tf_bI.restype = c_uint
        self.failUnlessEqual(testdll.tf_bI(0, 4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)

    def test_long(self):
        testdll.tf_l.restype = c_long
        testdll.tf_l.argtypes = (c_long,)
        self.failUnlessEqual(testdll.tf_l(-2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)

    def test_long_plus(self):
        testdll.tf_bl.restype = c_long
        testdll.tf_bl.argtypes = (c_byte, c_long)
        self.failUnlessEqual(testdll.tf_bl(0, -2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)

    def test_ulong(self):
        testdll.tf_L.restype = c_ulong
        self.failUnlessEqual(testdll.tf_L(4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)

    def test_ulong_plus(self):
        testdll.tf_bL.restype = c_ulong
        self.failUnlessEqual(testdll.tf_bL(0, 4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)

    def test_longlong(self):
        testdll.tf_q.restype = c_longlong
        testdll.tf_q.argtypes = (c_longlong, )
        self.failUnlessEqual(testdll.tf_q(-9223372036854775806), -3074457345618258602)
        self.failUnlessEqual(S(), -9223372036854775806)

    def test_longlong_plus(self):
        testdll.tf_bq.restype = c_longlong
        testdll.tf_bq.argtypes = (c_byte, c_longlong)
        self.failUnlessEqual(testdll.tf_bq(0, -9223372036854775806), -3074457345618258602)
        self.failUnlessEqual(S(), -9223372036854775806)

    def test_ulonglong(self):
        testdll.tf_Q.restype = c_ulonglong
        testdll.tf_Q.argtypes = (c_ulonglong, )
        self.failUnlessEqual(testdll.tf_Q(18446744073709551615), 6148914691236517205)
        self.failUnlessEqual(U(), 18446744073709551615)

    def test_ulonglong_plus(self):
        testdll.tf_bQ.restype = c_ulonglong
        testdll.tf_bQ.argtypes = (c_byte, c_ulonglong)
        self.failUnlessEqual(testdll.tf_bQ(0, 18446744073709551615), 6148914691236517205)
        self.failUnlessEqual(U(), 18446744073709551615)

    def test_float(self):
        testdll.tf_f.restype = c_float
        testdll.tf_f.argtypes = (c_float,)
        self.failUnlessEqual(testdll.tf_f(-42.), -14.)
        self.failUnlessEqual(S(), -42)

    def test_float_plus(self):
        testdll.tf_bf.restype = c_float
        testdll.tf_bf.argtypes = (c_byte, c_float)
        self.failUnlessEqual(testdll.tf_bf(0, -42.), -14.)
        self.failUnlessEqual(S(), -42)

    def test_double(self):
        testdll.tf_d.restype = c_double
        testdll.tf_d.argtypes = (c_double,)
        self.failUnlessEqual(testdll.tf_d(42.), 14.)
        self.failUnlessEqual(S(), 42)

    def test_double_plus(self):
        testdll.tf_bd.restype = c_double
        testdll.tf_bd.argtypes = (c_byte, c_double)
        self.failUnlessEqual(testdll.tf_bd(0, 42.), 14.)
        self.failUnlessEqual(S(), 42)

    def test_callwithresult(self):
        def process_result(result):
            return result * 2
        testdll.tf_i.restype = process_result
        testdll.tf_i.argtypes = (c_int,)
        self.failUnlessEqual(testdll.tf_i(42), 28)
        self.failUnlessEqual(S(), 42)
        self.failUnlessEqual(testdll.tf_i(-42), -28)
        self.failUnlessEqual(S(), -42)

    def test_void(self):
        testdll.tv_i.restype = None
        testdll.tv_i.argtypes = (c_int,)
        self.failUnlessEqual(testdll.tv_i(42), None)
        self.failUnlessEqual(S(), 42)
        self.failUnlessEqual(testdll.tv_i(-42), None)
        self.failUnlessEqual(S(), -42)

# The following repeates the above tests with stdcall functions (where
# they are available)
##try:
##    WinDLL
##except NameError:
##    pass
##else:
##    class stdcall_dll(WinDLL):
##        def __getattr__(self, name):
##            if name[:2] == '__' and name[-2:] == '__':
##                raise AttributeError, name
##            func = self._StdcallFuncPtr("s_" + name, self)
##            setattr(self, name, func)
##            return func

##    class stdcallCFunctions(CFunctions):

##        def __init__(self, *args):
##            unittest.TestCase.__init__(self, *args)
##            testdll = stdcall_dll(find_test_dll())

if __name__ == '__main__':
    unittest.main()
