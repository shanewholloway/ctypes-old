# Windows specific tests

from ctypes import *
import unittest, sys

if sys.platform == "win32":

    class WindowsTestCase(unittest.TestCase):
        def test_callconv_1(self):
            # Testing stdcall function

            IsWindow = windll.user32.IsWindow
            # ValueError: Procedure probably called with not enough arguments (4 bytes missing)
            self.assertRaises(ValueError, IsWindow)

            # This one should succeeed...
            self.failUnlessEqual(0, IsWindow(0))

            # ValueError: Procedure probably called with too many arguments (8 bytes in excess)
            self.assertRaises(ValueError, IsWindow, 0, 0, 0)

        def test_callconv_2(self):
            # Calling stdcall function as cdecl

            IsWindow = cdll.user32.IsWindow

            # ValueError: Procedure called with not enough arguments (4 bytes missing)
            # or wrong calling convention
            self.assertRaises(ValueError, IsWindow, None)

        def test_SEH(self):
            """Call functions with invalid arguments, and make sure that access violations
            are trapped and raise an exception"""
            # Normally, in a debug build of the _ctypes extension
            # module, exceptions are not trapped, so we can only run
            # this test in a release build.
            import sys
            if not hasattr(sys, "getobjects"):
                self.assertRaises(WindowsError, windll.kernel32.GetModuleHandleA, 32)

        # TODO: Add tests for passing structures (and unions?) by value.
        def test_struct_by_value(self):
            from ctypes.wintypes import POINT, RECT

            pt = POINT(10, 10)
            rect = RECT(0, 0, 20, 20)
            self.failUnlessEqual(True, windll.user32.PtInRect(byref(rect), pt))

if __name__ == '__main__':
    unittest.main()
