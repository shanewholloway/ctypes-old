import unittest, sys

class SimpleTypesTestCase(unittest.TestCase):

    def setUp(self):
        import ctypes
        try:
            from _ctypes import set_conversion_mode
        except ImportError:
            pass
        else:
            self.prev_conv_mode = set_conversion_mode("ascii", "strict")

    def tearDown(self):
        try:
            from _ctypes import set_conversion_mode
        except ImportError:
            pass
        else:
            set_conversion_mode(*self.prev_conv_mode)
        

    # XXX Replace by c_char_p tests
    def test_cstrings(self):
        from ctypes import c_char_p, byref

        # c_char_p.from_param on a Python String packs the string
        # into a cparam object
        s = "123"
        self.failUnless(c_char_p.from_param(s)._obj is s)

        # new in 0.9.1: convert (encode) unicode to ascii
        self.failUnlessEqual(c_char_p.from_param(u"123")._obj, "123")
        self.assertRaises(UnicodeEncodeError, c_char_p.from_param, u"123\377")

        self.assertRaises(TypeError, c_char_p.from_param, 42)

        # calling c_char_p.from_param with a c_char_p instance
        # returns the argument itself:
        a = c_char_p("123")
        self.failUnless(c_char_p.from_param(a) is a)

    def test_cw_strings(self):
        from ctypes import byref
        try:
            from ctypes import c_wchar_p
        except ImportError:
##            print "(No c_wchar_p)"
            return
        s = u"123"
        if sys.platform == "win32":
            self.failUnless(c_wchar_p.from_param(s)._obj is s)
            self.assertRaises(TypeError, c_wchar_p.from_param, 42)

            # new in 0.9.1: convert (decode) ascii to unicode
            self.failUnlessEqual(c_wchar_p.from_param("123")._obj, u"123")
        self.assertRaises(UnicodeDecodeError, c_wchar_p.from_param, "123\377")

        pa = c_wchar_p.from_param(c_wchar_p(u"123"))
        self.failUnlessEqual(type(pa), c_wchar_p)

    def test_int_pointers(self):
        from ctypes import c_short, c_uint, c_int, c_long, POINTER, pointer
        LPINT = POINTER(c_int)

##        p = pointer(c_int(42))
##        x = LPINT.from_param(p)
        x = LPINT.from_param(pointer(c_int(42)))
        self.failUnlessEqual(x.contents.value, 42)
        self.failUnlessEqual(LPINT(c_int(42)).contents.value, 42)

        self.failUnlessEqual(LPINT.from_param(None), 0)

        self.assertRaises(TypeError, LPINT.from_param, pointer(c_long(42)))
        self.assertRaises(TypeError, LPINT.from_param, pointer(c_uint(42)))
        self.assertRaises(TypeError, LPINT.from_param, pointer(c_short(42)))

    def test_byref_pointer(self):
        # The from_param class method of POINTER(typ) classes accepts what is
        # returned by byref(obj), it type(obj) == typ
        from ctypes import c_short, c_uint, c_int, c_long, pointer, POINTER, byref
        LPINT = POINTER(c_int)

        LPINT.from_param(byref(c_int(42)))

        self.assertRaises(TypeError, LPINT.from_param, byref(c_short(22)))
        self.assertRaises(TypeError, LPINT.from_param, byref(c_long(22)))
        self.assertRaises(TypeError, LPINT.from_param, byref(c_uint(22)))

    def test_byref_pointerpointer(self):
        # See above
        from ctypes import c_short, c_uint, c_int, c_long, pointer, POINTER, byref

        LPLPINT = POINTER(POINTER(c_int))
        LPLPINT.from_param(byref(pointer(c_int(42))))

        self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_short(22))))
        self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_long(22))))
        self.assertRaises(TypeError, LPLPINT.from_param, byref(pointer(c_uint(22))))

    def test_array_pointers(self):
        from ctypes import c_short, c_uint, c_int, c_long, POINTER
        INTARRAY = c_int * 3
        ia = INTARRAY()
        self.failUnlessEqual(len(ia), 3)
        self.failUnlessEqual([ia[i] for i in range(3)], [0, 0, 0])

        # Pointers are only compatible with arrays containing items of
        # the same type!
        LPINT = POINTER(c_int)
        LPINT.from_param((c_int*3)())
        self.assertRaises(TypeError, LPINT.from_param, c_short*3)
        self.assertRaises(TypeError, LPINT.from_param, c_long*3)
        self.assertRaises(TypeError, LPINT.from_param, c_uint*3)

##    def test_performance(self):
##        check_perf()

################################################################

def run_test(rep, msg, func, arg=None):
##    items = [None] * rep
    items = range(rep)
    from time import clock
    if arg is not None:
        start = clock()
        for _ in items:
            func(arg); func(arg); func(arg); func(arg); func(arg)
        stop = clock()
    else:
        start = clock()
        for _ in items:
            func(); func(); func(); func(); func()
        stop = clock()
    print "%15s: %.2f us" % (msg, ((stop-start)*1e6/5/rep))


def check_perf():
    # Convert 5 objects into parameters, using different approaches
    from ctypes import c_int

    REP = 1000000

    run_test(REP, "c_int.from_param(42)", c_int.from_param, 42)
    run_test(REP, "c_int.from_param(c_int(42))", c_int.from_param, c_int(42))

# Python 2.2 -OO, win2k, P4 700 MHz
#
#        c_int.from_param(42): 1.68 us
# c_int.from_param(c_int(42)): 0.62 us

# Python 2.3 -OO, win2k, P4 700 MHz
#
#        c_int.from_param(42): 1.01 us
# c_int.from_param(c_int(42)): 0.50 us

if __name__ == '__main__':
    import sys
    if '-p' in sys.argv:
        check_perf()
        sys.argv.remove('-p')
    unittest.main()
