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
        from ctypes import c_int, c_long, POINTER, pointer
        LPINT = POINTER(c_int)

        i = c_int(42)
        l = c_long(420)

        x = LPINT.from_param(pointer(i))        
        self.failUnless(x.contents.value == 42)
        self.failUnless(LPINT(i).contents.value == 42)

        self.failUnless(LPINT.from_param(None) == 0)

        self.assertRaises(TypeError, LPINT.from_param, pointer(l))

################################################################

def check_perf():
    # Convert 5 objects into parameters, using different approaches
    from time import clock
    from ctypes import c_int, POINTER, pointer, byref

    REP = 100000

    p = c_int(42)
    start = clock()
    for i in range(REP):
        byref(p); byref(p); byref(p); byref(p); byref(p)
    stop = clock()

    # My machine, win2k, Python 2.2: 1.38 us
    # My machine, win2k, Python 2.3: 0.68 us
    print "byref: %.2f us" % ((stop - start)*1e6/5/REP)

    f = c_int.from_param
    c = 42
    start = clock()
    for i in range(REP):
        f(c); f(c); f(c); f(c); f(c)
    stop = clock()

    # My machine, win2k, Python 2.2: 1.76 us
    # My machine, win2k, Python 2.3: 1.00 us
    print "from_param(42): %.2f us" % ((stop - start)*1e6/5/REP)

    f = c_int.from_param
    c = c_int(42)
    start = clock()
    for i in range(REP):
        f(c); f(c); f(c); f(c); f(c)
    stop = clock()

    # My machine, win2k, Python 2.2: 0.70 us
    # My machine, win2k, Python 2.3: 0.55 us
    print "from_param(c_int()): %.2f us" % ((stop - start)*1e6/5/REP)


def get_suite():
    return unittest.makeSuite(SimpleTypesTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    check_perf()
    unittest.main()
