import unittest

from ctypes import *

ctype_types = [c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint,
                 c_long, c_ulong, c_longlong, c_ulonglong, c_double, c_float]
python_types = [int, int, int, int, int, long,
                int, long, long, long, float, float]

class PointersTestCase(unittest.TestCase):
    def test_basics(self):
        from operator import delitem
        for ct, pt in zip(ctype_types, python_types):
            i = ct(42)
            p = pointer(i)
##            print type(p.contents), ct
            self.failUnless(type(p.contents) is ct)
            # p.contents is the same as p[0]
##            print p.contents
##            self.failUnless(p.contents == 42)
##            self.failUnless(p[0] == 42)

            self.assertRaises(TypeError, delitem, p, 0)

    def test_from_address(self):
        from array import array
        a = array('i', [100, 200, 300, 400, 500])
        addr = a.buffer_info()[0]

        p = POINTER(POINTER(c_int))
##        print dir(p)
##        print p.from_address
##        print p.from_address(addr)[0][0]

    def test_other(self):
        class Table(Structure):
            _fields_ = [("a", c_int),
                        ("b", c_int),
                        ("c", c_int)]

        pt = pointer(Table(1, 2, 3))

        self.failUnless(pt.contents.a == 1)
        self.failUnless(pt.contents.b == 2)
        self.failUnless(pt.contents.c == 3)

        pt.contents.c = 33
    
def get_suite():
    return unittest.makeSuite(PointersTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
