import unittest
from ctypes import *

class StringArrayTestCase(unittest.TestCase):
    def test(self):
        BUF = c_char * 4

        buf = BUF("a", "b", "c")
        self.failUnless(buf.value == "abc")
        self.failUnless(buf.raw == "abc\000")

        buf.value = "ABCD"
        self.failUnless(buf.value == "ABCD")
        self.failUnless(buf.raw == "ABCD")

        buf.value = "x"
        self.failUnless(buf.value == "x")
        self.failUnless(buf.raw == "x\000CD")

        buf[1] = "Z"
        self.failUnless(buf.value == "xZCD")
        self.failUnless(buf.raw == "xZCD")

        self.assertRaises(ValueError, setattr, buf, "value", "aaaaaaaa")
        self.assertRaises(TypeError, setattr, buf, "value", 42)

    def test_c_buffer_value(self):
        buf = c_buffer(32)

        buf.value = "Hello, World"
        self.failUnlessEqual(buf.value, "Hello, World")

        self.failUnlessRaises(TypeError, setattr, buf, "value", buffer("Hello, World"))
        self.assertRaises(TypeError, setattr, buf, "value", buffer("abc"))
        self.assertRaises(ValueError, setattr, buf, "raw", buffer("x" * 100))

    def test_c_buffer_raw(self):
        buf = c_buffer(32)

        buf.raw = buffer("Hello, World")
        self.failUnlessEqual(buf.value, "Hello, World")
        self.assertRaises(TypeError, setattr, buf, "value", buffer("abc"))
        self.assertRaises(ValueError, setattr, buf, "raw", buffer("x" * 100))

    def test_param_1(self):
        BUF = c_char * 4
        buf = BUF()
##        print c_char_p.from_param(buf)
        
    def test_param_2(self):
        BUF = c_char * 4
        buf = BUF()
##        print BUF.from_param(c_char_p("python"))
##        print BUF.from_param(BUF(*"pyth"))

class WStringArrayTestCase(unittest.TestCase):
    def test(self):
        BUF = c_wchar * 4

        buf = BUF(u"a", u"b", u"c")
        self.failUnless(buf.value == u"abc")

        buf.value = u"ABCD"
        self.failUnless(buf.value == u"ABCD")

        buf.value = u"x"
        self.failUnless(buf.value == u"x")

        buf[1] = u"Z"
        self.failUnless(buf.value == u"xZCD")

class StringTestCase(unittest.TestCase):
    def XX_test_basic_strings(self):
        cs = c_string("abcdef")

        # Cannot call len on a c_string any longer
        self.assertRaises(TypeError, len, cs)
        self.failUnless(sizeof(cs) == 7)

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

        self.assertRaises(TypeError, c_string, u"123")

    def XX_test_sized_strings(self):

        # New in releases later than 0.4.0: 
        self.assertRaises(TypeError, c_string, None)
        
        # New in releases later than 0.4.0:
        # c_string(number) returns an empty string of size number
        self.failUnless(len(c_string(32).raw) == 32)
        self.assertRaises(ValueError, c_string, -1)
        self.assertRaises(ValueError, c_string, 0)

        # These tests fail, because it is no longer initialized
##        self.failUnless(c_string(2).value == "")
##        self.failUnless(c_string(2).raw == "\000\000")
        self.failUnless(c_string(2).raw[-1] == "\000")
        self.failUnless(len(c_string(2).raw) == 2)

    def XX_test_initialized_strings(self):

        self.failUnless(c_string("ab", 4).raw[:2] == "ab")
        self.failUnless(c_string("ab", 4).raw[-1] == "\000")
        self.failUnless(c_string("ab", 2).raw == "a\000")

    def XX_test_toolong(self):
        cs = c_string("abcdef")
        # Much too long string:
        self.assertRaises(ValueError, setattr, cs, "value", "123456789012345")

        # One char too long values:
        self.assertRaises(ValueError, setattr, cs, "value", "1234567")

##    def test_perf(self):
##        check_perf()

class WStringTestCase(unittest.TestCase):
    def test_wchar(self):
        c_wchar(u"x")
        repr(byref(c_wchar(u"x")))
        c_wchar("x")
        

    def X_test_basic_wstrings(self):
        cs = c_wstring(u"abcdef")

        # XXX This behaviour is about to change:
        # len returns the size of the internal buffer in bytes.
        # This includes the terminating NUL character.
        self.failUnless(sizeof(cs) == 14)

        # The value property is the string up to the first terminating NUL.
        self.failUnless(cs.value == u"abcdef")
        self.failUnless(c_wstring(u"abc\000def").value == u"abc")

        self.failUnless(c_wstring(u"abc\000def").value == u"abc")

        # The raw property is the total buffer contents:
        self.failUnless(cs.raw == u"abcdef\000")
        self.failUnless(c_wstring(u"abc\000def").raw == u"abc\000def\000")

        # We can change the value:
        cs.value = u"ab"
        self.failUnless(cs.value == u"ab")
        self.failUnless(cs.raw == u"ab\000\000\000\000\000")

        self.assertRaises(TypeError, c_wstring, "123")
        self.assertRaises(ValueError, c_wstring, 0)

    def X_test_toolong(self):
        cs = c_wstring(u"abcdef")
        # Much too long string:
        self.assertRaises(ValueError, setattr, cs, "value", u"123456789012345")

        # One char too long values:
        self.assertRaises(ValueError, setattr, cs, "value", u"1234567")

        
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
    try:
        from ctypes import c_wchar
    except ImportError:
        return unittest.TestSuite((unittest.makeSuite(StringTestCase),
                                   unittest.makeSuite(StringArrayTestCase)))
    return unittest.TestSuite((unittest.makeSuite(StringTestCase),
                               unittest.makeSuite(WStringTestCase),
                               unittest.makeSuite(StringArrayTestCase)
##                               unittest.makeSuite(WStringArrayTestCase)
                              ))

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
##    check_perf()
##    unittest.main()
    test()
