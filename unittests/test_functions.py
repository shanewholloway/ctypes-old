from ctypes import *
import unittest

class FunctionTestCase(unittest.TestCase):

    def setUp(self):
        global dll
        import _ctypes
        dll = CDLL(_ctypes.__file__)

    def test_intresult(self):
        f = dll._testfunc_i_bhilfd
        f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double]
        result = f(1, 2, 3, 4, 5.0, 6.0)
        self.failUnless(result == 21)
        self.failUnless(type(result) == int)

        result = f(-1, -2, -3, -4, -5.0, -6.0)
        self.failUnless(result == -21)
        self.failUnless(type(result) == int)

        # If we declare the function to return a short,
        # is the high part split off?
        f.restype = "h"
        result = f(1, 2, 3, 4, 5.0, 6.0)
        self.failUnless(result == 21)
        self.failUnless(type(result) == int)
        
        result = f(1, 2, 3, 0x10004, 5.0, 6.0)
        self.failUnless(result == 21)
        self.failUnless(type(result) == int)

        # You cannot assing C datatypes as restype, except POINTER classes:
        self.assertRaises(TypeError, setattr, f, "restype", c_short)

    def test_floatresult(self):
        f = dll._testfunc_f_bhilfd
        f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double]
        f.restype = "f"
        result = f(1, 2, 3, 4, 5.0, 6.0)
        self.failUnless(result == 21)
        self.failUnless(type(result) == float)

        result = f(-1, -2, -3, -4, -5.0, -6.0)
        self.failUnless(result == -21)
        self.failUnless(type(result) == float)
        
    def test_doubleresult(self):
        f = dll._testfunc_d_bhilfd
        f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double]
        f.restype = "d"
        result = f(1, 2, 3, 4, 5.0, 6.0)
        self.failUnless(result == 21)
        self.failUnless(type(result) == float)

        result = f(-1, -2, -3, -4, -5.0, -6.0)
        self.failUnless(result == -21)
        self.failUnless(type(result) == float)
        
    def test_longlongresult(self):
        try:
            c_longlong
        except NameError:
            return
        f = dll._testfunc_q_bhilfd
        f.restype = "q"
        f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double]
        result = f(1, 2, 3, 4, 5.0, 6.0)
        self.failUnless(result == 21)
        self.failUnless(type(result) == long)

        f = dll._testfunc_q_bhilfdq
        f.restype = "q"
        f.argtypes = [c_byte, c_short, c_int, c_long, c_float, c_double, c_longlong]
        result = f(1, 2, 3, 4, 5.0, 6.0, 21)
        self.failUnless(result == 42)
        self.failUnless(type(result) == long)

    def test_stringresult(self):
        f = dll._testfunc_p_p
        f.restype = "z"
        result = f("123")
        self.failUnless(result == "123")

        result = f(None)
        self.failUnless(result == None)

    def test_pointers(self):
        f = dll._testfunc_p_p
        f.restype = POINTER(c_int)
        f.argtypes = [POINTER(c_int)]

        # This only works if the value c_int(42) passed to the
        # function is still alive while the pointer (the result) is
        # used.

        v = c_int(42)

        result = f(byref(v))
        self.failUnless(type(result) == POINTER(c_int))
        self.failUnless(result.contents.value == 42)

        # It is dangerous, however, because you don't control the lifetime
        # of the pointer:
        result = f(byref(c_int(99)))
        self.failUnless(result.contents.value != 99)

    def test_callbacks(self):
        f = dll._testfunc_callback_i_if
        f.restype = "i"

        class MyCallback(CFunction):
            _stdcall_ = 0
            _types_ = "i"

        def callback(value):
            #print "called back with", value
            return value
        
        cb = MyCallback(callback)
        result = f(-10, cb)
        self.failUnless(result == -18)

        # test with prototype
        f.argtypes = [c_int, MyCallback]
        cb = MyCallback(callback)
        result = f(-10, cb)
        self.failUnless(result == -18)
                
        class AnotherCallback(CFunction):
            _stdcall_ = 1
            _types_ = "iiii"

        # check that the prototype works: we call f with wrong
        # argument types
        cb = AnotherCallback(callback)
        self.assertRaises(TypeError, f, -10, cb)

def test_longlong_callbacks():
    # Currently not possible, it fails because there's no way to specify the
    # type of a callback function in argtypes!
##    """
##    >>> f = dll._testfunc_callback_q_qf
##    >>> f.restype = c_longlong
##    >>> class MyCallback(CFunction):
##    ...     _stdcall_ = 0
##    ...     _types_ = "q"

##    >>> f.argtypes = [c_longlong, MyCallback]
##    >>> def callback(value):
##    ...     print "called back with", value
    
##    >>> cb = MyCallback(callback)
##    >>> print dir(cb)
##    >>> print addressof(cb)

##    >>> # f(-10, cb._as_parameter_)

##    """
    ""
def get_suite():
    return unittest.makeSuite(FunctionTestCase, 'test')

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
