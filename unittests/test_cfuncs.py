import unittest
from ctypes import *

def find_test_dll():
    import sys, os
    if os.name == "nt":
        name = "_ctypes_test.pyd"
    else:
        name = "_ctypes_test.so"
    for p in sys.path:
        f = os.path.join(p, name)
        if os.path.isfile(f):
            return f

# These two functions report the argument in the last call to one of
# the tf_? functions.

from _ctypes_test import \
     get_last_tf_arg_s as S, \
     get_last_tf_arg_u as U

class CFunctions(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        self.dll = CDLL(find_test_dll())

    def test_byte(self):
        self.dll.tf_b.restype = c_byte
        self.dll.tf_b.argtypes = (c_byte,)
        self.failUnlessEqual(self.dll.tf_b(-126), -42)
        self.failUnlessEqual(S(), -126)
        self.dll.tf_bb.restype = c_byte
        self.dll.tf_bb.argtypes = (c_byte, c_byte)
        self.failUnlessEqual(self.dll.tf_bb(0, -126), -42)
        self.failUnlessEqual(S(), -126)

    def test_ubyte(self):
        self.dll.tf_B.restype = c_ubyte
        self.dll.tf_B.argtypes = (c_ubyte,)
        self.failUnlessEqual(self.dll.tf_B(255), 85)
        self.failUnlessEqual(U(), 255)
        self.dll.tf_bB.restype = c_ubyte
        self.dll.tf_bB.argtypes = (c_byte, c_ubyte)
        self.failUnlessEqual(self.dll.tf_bB(0, 255), 85)
        self.failUnlessEqual(U(), 255)

    def test_short(self):
        self.dll.tf_h.restype = c_short
        self.failUnlessEqual(self.dll.tf_h(-32766), -10922)
        self.failUnlessEqual(S(), -32766)
        self.dll.tf_bh.restype = c_short
        self.failUnlessEqual(self.dll.tf_bh(0, -32766), -10922)
        self.failUnlessEqual(S(), -32766)

    def test_ushort(self):
        self.dll.tf_H.restype = c_ushort
        self.failUnlessEqual(self.dll.tf_H(65535), 21845)
        self.failUnlessEqual(U(), 65535)
        self.dll.tf_bH.restype = c_ushort
        self.failUnlessEqual(self.dll.tf_bH(0, 65535), 21845)
        self.failUnlessEqual(U(), 65535)

    def test_int(self):
        self.dll.tf_i.restype = c_int
        self.failUnlessEqual(self.dll.tf_i(-2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)
        self.dll.tf_bi.restype = c_int
        self.failUnlessEqual(self.dll.tf_bi(0, -2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)

    def test_uint(self):
        self.dll.tf_I.restype = c_uint
        self.failUnlessEqual(self.dll.tf_I(4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)
        self.dll.tf_bI.restype = c_uint
        self.failUnlessEqual(self.dll.tf_bI(0, 4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)

    def test_long(self):
        self.dll.tf_l.restype = c_long
        self.dll.tf_l.argtypes = (c_long,)
        self.failUnlessEqual(self.dll.tf_l(-2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)
        self.dll.tf_bl.restype = c_long
        self.dll.tf_bl.argtypes = (c_byte, c_long)
        self.failUnlessEqual(self.dll.tf_bl(0, -2147483646), -715827882)
        self.failUnlessEqual(S(), -2147483646)

    def test_ulong(self):
        self.dll.tf_L.restype = c_ulong
        self.failUnlessEqual(self.dll.tf_L(4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)
        self.dll.tf_bL.restype = c_ulong
        self.failUnlessEqual(self.dll.tf_bL(0, 4294967295), 1431655765)
        self.failUnlessEqual(U(), 4294967295)

    def test_longlong(self):
        self.dll.tf_q.restype = c_longlong
        self.dll.tf_q.argtypes = (c_longlong, )
        self.failUnlessEqual(self.dll.tf_q(-9223372036854775806), -3074457345618258602)
        self.failUnlessEqual(S(), -9223372036854775806)
        self.dll.tf_bq.restype = c_longlong
        self.dll.tf_bq.argtypes = (c_byte, c_longlong)
        self.failUnlessEqual(self.dll.tf_bq(0, -9223372036854775806), -3074457345618258602)
        self.failUnlessEqual(S(), -9223372036854775806)

    def test_ulonglong(self):
        self.dll.tf_Q.restype = c_ulonglong
        self.dll.tf_Q.argtypes = (c_ulonglong, )
        self.failUnlessEqual(self.dll.tf_Q(18446744073709551615), 6148914691236517205)
        self.failUnlessEqual(U(), 18446744073709551615)
        self.dll.tf_bQ.restype = c_ulonglong
        self.dll.tf_bQ.argtypes = (c_byte, c_ulonglong)
        self.failUnlessEqual(self.dll.tf_bQ(0, 18446744073709551615), 6148914691236517205)
        self.failUnlessEqual(U(), 18446744073709551615)

    def test_float(self):
        self.dll.tf_f.restype = c_float
        self.dll.tf_f.argtypes = (c_float,)
        self.failUnlessEqual(self.dll.tf_f(-42.), -14.)
        self.failUnlessEqual(S(), -42)
        self.dll.tf_bf.restype = c_float
        self.dll.tf_bf.argtypes = (c_byte, c_float)
        self.failUnlessEqual(self.dll.tf_bf(0, -42.), -14.)
        self.failUnlessEqual(S(), -42)

    def test_double(self):
        self.dll.tf_d.restype = c_double
        self.dll.tf_d.argtypes = (c_double,)
        self.failUnlessEqual(self.dll.tf_d(42.), 14.)
        self.failUnlessEqual(S(), 42)
        self.dll.tf_bd.restype = c_double
        self.dll.tf_bd.argtypes = (c_byte, c_double)
        self.failUnlessEqual(self.dll.tf_bd(0, 42.), 14.)
        self.failUnlessEqual(S(), 42)

    def test_callwithresult(self):
        def process_result(result):
            return result * 2
        self.dll.tf_i.restype = process_result
        self.dll.tf_i.argtypes = (c_int,)
        self.failUnlessEqual(self.dll.tf_i(42), 28)
        self.failUnlessEqual(S(), 42)
        self.failUnlessEqual(self.dll.tf_i(-42), -28)
        self.failUnlessEqual(S(), -42)

    def test_void(self):
        self.dll.tv_i.restype = None
        self.dll.tv_i.argtypes = (c_int,)
        self.failUnlessEqual(self.dll.tv_i(42), None)
        self.failUnlessEqual(S(), 42)
        self.failUnlessEqual(self.dll.tv_i(-42), None)
        self.failUnlessEqual(S(), -42)

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
            self.dll = stdcall_dll(find_test_dll())

if __name__ == '__main__':
    unittest.main()
