from ctypes import *
import unittest, sys

def callback_func(arg):
    42 / arg
    raise ValueError, arg

class CallbackTracbackTestCase(unittest.TestCase):
    # When an exception is raised in a ctypes callback function, the C
    # code prints a traceback.
    #
    # This test makes sure the exception types *and* the exception
    # value is printed correctly - the exception value is converted
    # into a string, and '(in callback)' is prepended to it.

    def capture_stderr(self, func, *args, **kw):
        # helper - call function 'func', and return the captured stderr
        import StringIO
        logger = sys.stderr = StringIO.StringIO()
        try:
            func(*args, **kw)
        finally:
            sys.stderr = sys.__stderr__
        return logger.getvalue()

    def test_ValueError(self):
        cb = CFUNCTYPE(c_int, c_int)(callback_func)
        out = self.capture_stderr(cb, 42)
        self.failUnlessEqual(out.splitlines()[-1],
                             "ValueError: (in callback) 42")

    def test_IntegerDivisionError(self):
        cb = CFUNCTYPE(c_int, c_int)(callback_func)
        out = self.capture_stderr(cb, 0)
        self.failUnlessEqual(out.splitlines()[-1],
              "ZeroDivisionError: (in callback) integer division or modulo by zero")

    def test_FloatDivisionError(self):
        cb = CFUNCTYPE(c_int, c_double)(callback_func)
        out = self.capture_stderr(cb, 0.0)
        self.failUnlessEqual(out.splitlines()[-1],
                             "ZeroDivisionError: (in callback) float division")

    def test_TypeErrorDivisionError(self):
        cb = CFUNCTYPE(c_int, c_char_p)(callback_func)
        out = self.capture_stderr(cb, "spam")
        self.failUnlessEqual(out.splitlines()[-1],
              "TypeError: (in callback) unsupported operand type(s) for /: 'int' and 'str'")

if sys.platform == "win32":
    def __del__(self):
        pass

    class MyTestCase(unittest.TestCase):
        # This test makes sure that calling a COM method on a COM
        # interface pointer raises a ValueError, when the interface
        # pointer points to NULL.

        def setUp(self):
            from ctypes.com import IUnknown
            self._orig_del = POINTER(IUnknown).__del__
            # We replace the __del__ method (which calls self.Release(),
            # because it would crash.
            POINTER(IUnknown).__del__ = __del__

        def tearDown(self):
            from ctypes.com import IUnknown
            POINTER(IUnknown).__del__ = self._orig_del

        def test_comcrash(self):
            from ctypes.com import IUnknown
            p = pointer(IUnknown())
            try:
                p.AddRef()
            except ValueError, message:
                self.failUnlessEqual(str(message), "COM method call without VTable")
            else:
                self.fail("Exception expected")

if __name__ == '__main__':
    unittest.main()
