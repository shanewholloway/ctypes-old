import unittest

from ctypes import *

numeric_types = [c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint,
                 c_long, c_ulong, c_longlong, c_ulonglong, c_double, c_float]

class PointersTestCase(unittest.TestCase):
    def test_basics(self):
        for t in numeric_types:
            i = t(42)
            p = pointer(i)
            self.failUnless(type(p.contents) is t)
            # p.contents is the same as p[0]
            self.failUnless(p.contents.value == 42)
            self.failUnless(p[0].value == 42)

    def test_from_address(self):
        from array import array
        a = array('i', [100, 200, 300, 400, 500])
        addr = a.buffer_info()[0]

        p = POINTER(POINTER(c_int))
##        print dir(p)
##        print p.from_address
##        print p.from_address(addr)[0][0]
    
def get_suite():
    return unittest.makeSuite(PointersTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
