import unittest
from ctypes import * # bad style, generally

class CFuncPtrTestCase(unittest.TestCase):
    def test_basic(self):
        # no, CFuncPtr has no size, but it's subclasses
##        self.failUnless(sizeof(CFuncPtr) == sizeof(c_voidp))

        class X(CFuncPtr):
            _flags_ = 0
            _restype_ = c_int
            _argtypes_ = c_int, c_int

        def func(*args):
            return len(args)

        x = X(func)
        self.failUnless(sizeof(x) == sizeof(c_voidp))
        self.failUnless(sizeof(X) == sizeof(c_voidp))

    def test_first(self):
        class StdCallback(CFuncPtr):
            _flags_ = 0
            _argtypes_ = c_int, c_int

        class CdeclCallback(CFuncPtr):
            _flags_ = FUNCFLAG_CDECL
            _argtypes_ = c_int, c_int

        def func(a, b):
            return a + b

        s = StdCallback(func)
        c = CdeclCallback(func)

        self.failUnless(s(1, 2) == 3)
        self.failUnless(c(1, 2) == 3)
        self.assertRaises(TypeError, s, 1, 2, 3)
        self.assertRaises(TypeError, c, 1, 2, 3)

    def test_structures(self):
        class WNDPROC(CFuncPtr):
            _argtypes_ = c_int, c_int, c_int, c_int
            _restype_ = c_long
            _flags_ = FUNCFLAG_STDCALL

        def wndproc(hwnd, msg, wParam, lParam):
            return hwnd + msg + wParam + lParam

        HINSTANCE = c_int
        HICON = c_int
        HCURSOR = c_int
        LPCTSTR = c_char_p

        class WNDCLASS(Structure):
            _fields_ = [("style", c_uint),
                        ("lpfnWndProc", WNDPROC),
                        ("cbClsExtra", c_int),
                        ("cbWndExtra", c_int),
                        ("hInstance", HINSTANCE),
                        ("hIcon", HICON),
                        ("hCursor", HCURSOR),
                        ("lpszMenuName", LPCTSTR),
                        ("lpszClassName", LPCTSTR)]

        wndclass = WNDCLASS()
        wndclass.lpfnWndProc = WNDPROC(wndproc)

        class WNDPROC_2(CFuncPtr):
            _argtypes_ = c_int, c_int, c_int, c_int
            _restype_ = c_long
            _flags_ = FUNCFLAG_STDCALL

        # CFuncPtr subclasses are compared by identity, so this raises a TypeError:
##        wndclass.lpfnWndProc = WNDPROC_2(wndproc)
        self.assertRaises(TypeError, setattr, wndclass,
                          "lpfnWndProc", WNDPROC_2(wndproc))

        self.failUnless(wndclass.lpfnWndProc(1, 2, 3, 4) == 10)

        f = wndclass.lpfnWndProc

        del wndclass
        del wndproc

        self.failUnless(f(10, 11, 12, 13) == 46)


    # non-working tests

    def _test_prototypes(self):
        func = windll.kernel32.GetModuleHandleA

        self.failUnless(func.restype == None)
        self.failUnless(func.argtypes == None)

        func.restype = c_int
        self.failUnless(func.restype == c_int)

        func.argtypes = (c_char_p,)
        self.failUnless(func.argtypes == (c_char_p,))

    def _test_prototypes_2(self):
        class X(CFuncPtr):
            _flags_ = 0
            _restype_ = c_int
            _argtypes_ = c_int, c_int

        def func(*args):
            return len(args)

        x = X(func)

        self.failUnless(x.argtypes == (c_int, c_int))
        self.failUnless(x.restype == c_int)

        # For CFuncPtr subclasses, argtypes and restype are readonly
        self.assertRaises(AttributeError, setattr, x, "argtypes", ())
        self.assertRaises(AttributeError, setattr, x, "restype", c_int)

def get_suite():
    return unittest.makeSuite(CFuncPtrTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
