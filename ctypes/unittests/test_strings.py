import unittest

class StringTestCase(unittest.TestCase):
    def test_basic_strings(self):
        from ctypes import c_string
        cs = c_string("abcdef")

        # XXX Thsi behaviour is about to change:
        # len returns the size of the internal buffer in bytes.
        # This includes the terminating NUL character.
        self.failUnless(len(cs) == 7)

        # The value property is the string up to the first terminating NUL.
        self.failUnless(cs.value == "abcdef")
        self.failUnless(c_string("abc\000def").value == "abc")

        # The raw property is the total buffer contents:
        self.failUnless(cs.raw == "abcdef\000")
        self.failUnless(c_string("abc\000def").raw == "abc\000def\000")

        # We can change the value:
        cs.value = "ab"
        self.failUnless(cs.value == "ab")
        self.failUnless(cs.raw == "ab\000\000\000\000\000")

        cs.raw = "XY"
        self.failUnless(cs.value == "XY")
        self.failUnless(cs.raw == "XY\000\000\000\000\000")

    def test_toolong(self):
        from ctypes import c_string
        cs = c_string("abcdef")
        # Much too long string:
        self.assertRaises(ValueError, setattr, cs, "value", "123456789012345")

        # One char too long values:
        self.assertRaises(ValueError, setattr, cs, "value", "1234567")

##    def test_perf(self):
##        check_perf()

class UNUSED:
    def test_basic_wstrings(self):
        from ctypes import c_wstring
        cs = c_wstring(u"abcdef")

        # XXX Thsi behaviour is about to change:
        # len returns the size of the internal buffer in bytes.
        # This includes the terminating NUL character.
        self.failUnless(len(cs) == 14)

        # The value property is the string up to the first terminating NUL.
        print repr(cs.value)
        self.failUnless(cs.value == u"abcdef")
        self.failUnless(c_string("abc\000def").value == "abc")

        # The raw property is the total buffer contents:
        self.failUnless(cs.raw == "abcdef\000")
        self.failUnless(c_string("abc\000def").raw == "abc\000def\000")

        # We can change the value:
        cs.value = "ab"
        self.failUnless(cs.value == "ab")
        self.failUnless(cs.raw == "ab\000\000\000\000\000")


    def test_toolong(self):
        from ctypes import c_string
        cs = c_string("abcdef")
        # Much too long string:
        self.assertRaises(ValueError, setattr, cs, "value", "123456789012345")

        # One char too long values:
        self.assertRaises(ValueError, setattr, cs, "value", "1234567")

        
def run_test(rep, msg, func, arg):
    items = range(rep)
    from time import clock
    start = clock()
    for i in items:
        func(arg); func(arg); func(arg); func(arg); func(arg)
    stop = clock()
    print "%20s: %.2f us" % (msg, ((stop-start)*1e6/5/rep))

def check_perf():
    # Construct 5 objects
    from ctypes import c_string

    REP = 200000

    run_test(REP, "c_string(None)", c_string, None)
    run_test(REP, "c_string('abc')", c_string, 'abc')

# Python 2.3 -OO, win2k, P4 700 MHz:
#
#      c_string(None): 1.75 us
#     c_string('abc'): 2.74 us

# Python 2.2 -OO, win2k, P4 700 MHz:
#
#      c_string(None): 2.95 us
#     c_string('abc'): 3.67 us

def get_suite():
    import unittest
    return unittest.makeSuite(StringTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    check_perf()
    unittest.main()
