import unittest

from ctypes import *

ctype_types = [c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint,
                 c_long, c_ulong, c_longlong, c_ulonglong, c_double, c_float]
python_types = [int, int, int, int, int, long,
                int, long, long, long, float, float]

class PointersTestCase(unittest.TestCase):
    def test_pass_pointers(self):
        import _ctypes
        dll = CDLL(_ctypes.__file__)
        func = dll._testfunc_p_p

        i = c_int(12345678)
##        func.argtypes = (POINTER(c_int),)
        address = func(byref(i))
        self.failUnless(c_int.from_address(address).value == 12345678)

        func.restype = POINTER(c_int)
        res = func(pointer(i))
        self.failUnless(res.contents.value == 12345678)
        self.failUnless(res[0] == 12345678)

    def test_change_pointers(self):
        import _ctypes
        dll = CDLL(_ctypes.__file__)
        func = dll._testfunc_p_p

        i = c_int(87654)
        func.restype = POINTER(c_int)
        func.argtypes = (POINTER(c_int),)

        res = func(pointer(i))
        self.failUnless(res[0] == 87654)
        self.failUnless(res.contents.value == 87654)

        # C code: *res = 54345
        res[0] = 54345
        self.failUnless(i.value == 54345)

        # C code:
        #   int x = 12321;
        #   res = &x
        res.contents = c_int(12321)
        self.failUnless(i.value == 54345)

    def test_callbacks_with_pointers(self):
        # a function type receiving a pointer
        PROTOTYPE = CFUNCTYPE(c_int, POINTER(c_int))

        self.result = []

        def func(arg):
            for i in range(10):
##                print arg[i],
                self.result.append(arg[i])
            print
            return 0
        callback = PROTOTYPE(func)

        import _ctypes
        dll = CDLL(_ctypes.__file__)
        # This function expects a function pointer,
        # and calls this with an integer pointer as parameter.
        # The int pointer points to a table containing the numbers 1..10
        doit = dll._testfunc_callback_with_pointer

##        i = c_int(42)
##        callback(byref(i))
##        self.failUnless(i.value == 84)

        doit(callback)
##        print self.result
        doit(callback)
##        print self.result
        
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
