import unittest, os
from ctypes import *

class RECT(Structure):
    _fields_ = [("left", c_long),
                ("top", c_long),
                ("right", c_long),
                ("bottom", c_long)]

    def __repr__(self):
        return "<RECT(%d, %d, %d, %d) at %x>" % (self.left,
                                                 self.top,
                                                 self.right,
                                                 self.bottom,
                                                 id(self))

class BOOL(c_long):
    def check_retval(self, val):
        if val == 0:
            # WindowsError would be bettter, but the tests must run
            # crossplatform
            raise ValueError(val)
    _check_retval_ = classmethod(check_retval)

class Test(unittest.TestCase):

    def test_invalid_paramflags(self):
        import _ctypes_test
        dll = CDLL(_ctypes_test.__file__)

        proto = CFUNCTYPE(c_int, POINTER(c_int))

        # Hm, I should look into doctest's unittest integration.
        # Doctest makes it easy to check for actual error messages.

        # ValueError: paramflags must have the same length as argtypes
        self.failUnlessRaises(ValueError,
                              lambda: proto("TwoOutArgs", dll,
                                            ()))

        # TypeError: paramflags must be a sequence of (int [,string [,value]]) tuples
        self.failUnlessRaises(TypeError, lambda: proto("TwoOutArgs", dll, ((1, 2, 3),)))

        proto = CFUNCTYPE(c_int, c_int)
        # TypeError: output parameter 1 not a pointer type: c_long
        self.failUnlessRaises(TypeError, lambda: proto("TwoOutArgs", dll, ((2,),)))

        # These are correct
        proto = CFUNCTYPE(c_int, POINTER(c_int))
        proto("TwoOutArgs", dll,
              ((1,),)
              )
        proto("TwoOutArgs", dll,
              ((1, "paramname"),)
              )
        proto("TwoOutArgs", dll,
              ((1, "paramname", 'DefaultVal'),)
              )
        # We CAN pass None instead of the paramflags tuple
        proto("TwoOutArgs", dll, None)
        # and we CAN pass None instead of the parameter names
        proto("TwoOutArgs", dll,
              ((1, None),)
              )
        proto("TwoOutArgs", dll,
              ((1, None, 'DefaultVal'),)
              )


    def test_usage_sample(self):
        import _ctypes_test
        dll = CDLL(_ctypes_test.__file__)

        hwnd_desktop = dll.my_GetDesktopWindow()

        proto = CFUNCTYPE(BOOL, c_long, POINTER(RECT))
        func = proto("my_GetWindowRect", dll, ((1, "hwnd"), (2,)))

        # returns a RECT instance...
        self.assertEqual(type(func(hwnd_desktop)), RECT)
        # ...unless the call fails
        self.assertRaises(ValueError, lambda: func(0))
        # TypeError: required argument 'hwnd' missing
        self.assertRaises(TypeError, lambda: func())
        # TypeError: call takes exactly 1 arguments (3 given)
        self.assertRaises(TypeError, lambda: func(0, 1, 2))
        # TypeError: required argument 'hwnd' missing
        self.assertRaises(TypeError, lambda: func(spam=hwnd_desktop))
        # TypeError: call takes exactly 1 arguments (2 given)
        self.assertRaises(TypeError, lambda: func(hwnd=hwnd_desktop, spam=32))

    
    if os.name == "nt":
        def test_usage_sample_WIN32(self):
            hwnd_desktop = windll.user32.GetDesktopWindow()

            proto = WINFUNCTYPE(BOOL, c_long, POINTER(RECT))
            func = proto("GetWindowRect", windll.user32, ((1, "hwnd"), (2,)))

            # returns a RECT instance...
            self.assertEqual(type(func(hwnd_desktop)), RECT)
            # returns a RECT instance...
            self.assertEqual(type(func(hwnd=hwnd_desktop)), RECT)
            # ...unless the call fails
            self.assertRaises(ValueError, lambda: func(0))
            # TypeError: required argument 'hwnd' missing
            self.assertRaises(TypeError, lambda: func())
            # TypeError: call takes exactly 1 arguments (3 given)
            self.assertRaises(TypeError, lambda: func(0, 1, 2))
            # TypeError: required argument 'hwnd' missing
            self.assertRaises(TypeError, lambda: func(spam=hwnd_desktop))
            # TypeError: call takes exactly 1 arguments (2 given)
            self.assertRaises(TypeError, lambda: func(hwnd=hwnd_desktop, spam=32))

        def test_default_args(self):
            windll.kernel32.GetModuleHandleW

            proto = WINFUNCTYPE(c_long, c_wchar_p)
            func = proto("GetModuleHandleW", windll.kernel32,
                         ((1, "lpModuleName", None),))
            func(lpModuleName="kernel32")
            func("kernel32")
            func(None)
            func()
            # XXX Problem with error messages here.
            # Since the arguments are only counted,
            # this is the error you will get:
            # TypeError: call takes exactly 0 arguments (1 given)
            #func(a=1)

    def test_multiple_outargs(self):
        import _ctypes_test
        dll = CDLL(_ctypes_test.__file__)

        # the COM idl of this function would be:
        # void TwoOutArgs([in] int a, [out] int *p1, [in] int b, [out] int *p2);
        proto = CFUNCTYPE(None, c_int, POINTER(c_int), c_int, POINTER(c_int))
        func = proto("TwoOutArgs", dll, ((1, "a"), (2, "p1"), (1, "b"), (2, "p2")))
        self.failUnlessEqual((1, 2), func(1, 2))
        self.failUnlessEqual((1, 2), func(b=2, a=1))

    def test_inout_args(self):
        import _ctypes_test
        dll = CDLL(_ctypes_test.__file__)

        # the COM idl of this function would be:
        # void TwoOutArgs([in] int a, [in, out] int *p1, [in] int b, [in, out] int *p2);
        proto = CFUNCTYPE(None, c_int, POINTER(c_int), c_int, POINTER(c_int))
        func = proto("TwoOutArgs", dll, ((1, "a"), (3, "p1"), (1, "b"), (3, "p2")))
        # The function returns ((a + p1), (b + p2))
        self.failUnlessEqual((3, 7), func(1, 2, 3, 4))
        self.failUnlessEqual((10, 14), func(a=1, b=3, p1=9, p2=11))
        # TypeError: required argument 'p1' is missing
        self.assertRaises(TypeError, lambda: func(a=1, b=3))
        # TypeError: required argument 'p2' is missing
        self.assertRaises(TypeError, lambda: func(a=1, b=3, p1=3))

def get_inout_args_func():
    """
    Error messages may be somewhat confusing, when parameters are
    missing.  This example shows how the error messsages differ from
    normal Python functions.  The reason is the way arguments are
    processed when paramflags are present, and named arguments are
    used.

    We construct two functions having the same signature:
    
    >>> def p(a, b, c, d):
    ...     return a+c, b+d
    ...
    >>> f = get_inout_args_func()
    >>> f(a=1, b=3) # ctypes function
    Traceback (most recent call last):
      ...
    TypeError: required argument 'p1' missing
    >>> p(a=1, b=3) # normal python function
    Traceback (most recent call last):
      ...
    TypeError: p() takes exactly 4 non-keyword arguments (2 given)
    >>>
    >>> f(1, 2)
    Traceback (most recent call last):
      ...
    TypeError: required argument 'b' missing
    >>> f(1, 2, 3, 4)
    (3, 7)
    >>> f(x=1, y=2)
    Traceback (most recent call last):
      ...
    TypeError: required argument 'a' missing
    >>> p(x=1, y=2)
    Traceback (most recent call last):
      ...
    TypeError: p() got an unexpected keyword argument 'x'
    >>>

    >>> f("x", "y")
    Traceback (most recent call last):
      ...
    TypeError: int expected instead of str instance
    >>>

    # The following examples show problems with the error messages:
    
    >>> f(a=1, b="y", p1=3, p2=4)
    Traceback (most recent call last):
      ...
    ArgumentError: argument 3: exceptions.TypeError: int expected instead of str instance
    >>> f(a=1, b=2, p1="3", p2=4)
    Traceback (most recent call last):
      ...
    TypeError: int expected instead of str instance
    >>>
    """
    import _ctypes_test
    dll = CDLL(_ctypes_test.__file__)
    # void TwoOutArgs([in] int a, [in, out] int *p1, [in] int b, [in, out] int *p2);
    proto = CFUNCTYPE(None, c_int, POINTER(c_int), c_int, POINTER(c_int))
    func = proto("TwoOutArgs", dll, ((1, "a"), (3, "p1"), (1, "b"), (3, "p2")))
    return func


if __name__ == "__main__":
    unittest.main()