import unittest

class SimpleTypesTestCase(unittest.TestCase):

    def test_cstrings(self):
        from ctypes import c_string, byref

        # c_string.from_param on a Python String returns the argument
        s = "123"
        self.failUnless(c_string.from_param(s) is s)

        self.assertRaises(TypeError, c_string.from_param, u"123")
        self.assertRaises(TypeError, c_string.from_param, 42)

        # calling c_string.from_param with a c_string instance
        # returns the argument itself:
        a = c_string("123")
        self.failUnless(c_string.from_param(a) is a)

        self.failUnless(c_string.from_param(None) == 0)

        # Since c_string instances are always passed by reference,
        # calling byref() with them raises an error (XXX although
        # the error message should be fixed: 'expected CData instance'
        self.assertRaises(TypeError, byref, c_string("123"))
        self.assertRaises(TypeError, byref, "123")

        # Hm, how to check the c_string(xxx)._as_parameter_ attribute?


    def test_cw_strings(self):
        from ctypes import byref
        try:
            from ctypes import c_wstring
        except ImportError:
##            print "(No c_wstring)"
            return
        self.failUnless(c_wstring.from_param(u"123") == u"123")

        self.assertRaises(TypeError, c_wstring.from_param, "123")
        self.assertRaises(TypeError, c_wstring.from_param, 42)

        pa = c_wstring.from_param(c_wstring(u"123"))
        self.failUnless(type(pa) == c_wstring)
        self.failUnless(c_wstring.from_param(None) == 0)

        # Since c_wstring instances are always passed by reference,
        # byref() raises an error:
        self.assertRaises(TypeError, byref, c_wstring(u"123"))
        self.assertRaises(TypeError, byref, u"123")

        # Hm, how to check the c_wstring(xxx)._as_parameter_ attribute?

    def test_int_pointers(self):
        from ctypes import c_short, c_uint, c_int, c_long, POINTER, pointer
        LPINT = POINTER(c_int)

##        p = pointer(c_int(42))
##        x = LPINT.from_param(p)
        x = LPINT.from_param(pointer(c_int(42)))
        self.failUnless(x.contents.value == 42)
        self.failUnless(LPINT(c_int(42)).contents.value == 42)

        self.failUnless(LPINT.from_param(None) == 0)

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
        self.failUnless(len(ia) == 3)
        self.failUnless([ia[i] for i in range(3)] == [0, 0, 0])

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

def get_suite():
    return unittest.makeSuite(SimpleTypesTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    import sys
    if '-p' in sys.argv:
        check_perf()
        sys.argv.remove('-p')
    unittest.main()
