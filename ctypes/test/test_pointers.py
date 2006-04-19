import unittest

from ctypes import *
import _ctypes_test

ctype_types = [c_byte, c_ubyte, c_short, c_ushort, c_int, c_uint,
                 c_long, c_ulong, c_longlong, c_ulonglong, c_double, c_float]
python_types = [int, int, int, int, int, long,
                int, long, long, long, float, float]

class PointersTestCase(unittest.TestCase):

    def test_pointer_crash(self):

        class A(POINTER(c_ulong)):
            pass

        POINTER(c_ulong)(c_ulong(22))
        # Pointer can't set contents: has no _type_
        self.failUnlessRaises(TypeError, A, c_ulong(33))

    def test_pass_pointers(self):
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_p_p
        func.restype = c_long

        i = c_int(12345678)
##        func.argtypes = (POINTER(c_int),)
        address = func(byref(i))
        self.failUnlessEqual(c_int.from_address(address).value, 12345678)

        func.restype = POINTER(c_int)
        res = func(pointer(i))
        self.failUnlessEqual(res.contents.value, 12345678)
        self.failUnlessEqual(res[0], 12345678)

    def test_change_pointers(self):
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_p_p

        i = c_int(87654)
        func.restype = POINTER(c_int)
        func.argtypes = (POINTER(c_int),)

        res = func(pointer(i))
        self.failUnlessEqual(res[0], 87654)
        self.failUnlessEqual(res.contents.value, 87654)

        # C code: *res = 54345
        res[0] = 54345
        self.failUnlessEqual(i.value, 54345)

        # C code:
        #   int x = 12321;
        #   res = &x
        res.contents = c_int(12321)
        self.failUnlessEqual(i.value, 54345)

    def test_callbacks_with_pointers(self):
        # a function type receiving a pointer
        PROTOTYPE = CFUNCTYPE(c_int, POINTER(c_int))

        self.result = []

        def func(arg):
            for i in range(10):
##                print arg[i],
                self.result.append(arg[i])
##            print
            return 0
        callback = PROTOTYPE(func)

        dll = CDLL(_ctypes_test.__file__)
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

        self.failUnlessEqual(pt.contents.a, 1)
        self.failUnlessEqual(pt.contents.b, 2)
        self.failUnlessEqual(pt.contents.c, 3)

        pt.contents.c = 33

        from ctypes import _pointer_type_cache
        del _pointer_type_cache[Table]

    def test_basic(self):
        p = pointer(c_int(42))
        # Although a pointer can be indexed, it ha no length
        self.assertRaises(TypeError, len, p)
        self.failUnlessEqual(p[0], 42)
        self.failUnlessEqual(p.contents.value, 42)

    def test_incomplete(self):
        lpcell = POINTER("cell")
        class cell(Structure):
            _fields_ = [("value", c_int),
                        ("next", lpcell)]
        SetPointerType(lpcell, cell)

        # Make a structure containing a pointer to itself:
        c = cell()
        c.value = 42
        c.next = pointer(c)

        result = []
        for i in range(8):
            result.append(c.value)
            c = c.next[0]
        self.failUnlessEqual(result, [42] * 8)

        from ctypes import _pointer_type_cache
        del _pointer_type_cache[cell]

    def test_charpp( self ):
        """Test that a character pointer-to-pointer is correctly passed"""
        dll = CDLL(_ctypes_test.__file__)
        func = dll._testfunc_c_p_p
        func.restype = c_char_p
        argv = (c_char_p * 2)()
        argc = c_int( 2 )
        argv[0] = 'hello'
        argv[1] = 'world'
        result = func( byref(argc), argv )
        assert result == 'world', result

    def test_bug_1467852(self):
        # http://sourceforge.net/tracker/?func=detail&atid=532154&aid=1467852&group_id=71702
        x = c_int(5)
        dummy = []
        for i in range(32000):
            dummy.append(c_int(i))
        y = c_int(6)
        p = pointer(x)
        pp = pointer(p)
        q = pointer(y)
        pp[0] = q         # <==
        self.failUnlessEqual(p[0], 6)

if __name__ == '__main__':
    unittest.main()