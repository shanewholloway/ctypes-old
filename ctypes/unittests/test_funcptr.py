import unittest
from ctypes import * # bad style, generally

class CFuncPtrTestCase(unittest.TestCase):
    def test_basic(self):
        X = WinFuncType(c_int, c_int, c_int)

        def func(*args):
            return len(args)

        x = X(func)
        self.failUnless(sizeof(x) == sizeof(c_voidp))
        self.failUnless(sizeof(X) == sizeof(c_voidp))

    def test_first(self):
        StdCallback = WinFuncType(c_int, c_int, c_int)
        CdeclCallback = CFuncType(c_int, c_int, c_int)

        def func(a, b):
            return a + b

        s = StdCallback(func)
        c = CdeclCallback(func)

        self.failUnless(s(1, 2) == 3)
        self.failUnless(c(1, 2) == 3)
        self.assertRaises(TypeError, s, 1, 2, 3)
        self.assertRaises(TypeError, c, 1, 2, 3)

    def test_structures(self):
        WNDPROC = WinFuncType(c_long, c_int, c_int, c_int, c_int)

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

        WNDPROC_2 = WinFuncType(c_long, c_int, c_int, c_int, c_int)

        # CFuncPtr subclasses are compared by identity, so this raises a TypeError:
##        wndclass.lpfnWndProc = WNDPROC_2(wndproc)
        self.assertRaises(TypeError, setattr, wndclass,
                          "lpfnWndProc", WNDPROC_2(wndproc))

        self.failUnless(wndclass.lpfnWndProc(1, 2, 3, 4) == 10)

        f = wndclass.lpfnWndProc

        del wndclass
        del wndproc

        self.failUnless(f(10, 11, 12, 13) == 46)

    def test_dllfunctions(self):

        def NoNullHandle(value):
            if not value:
                raise WinError()
            return value

        f = windll.kernel32.GetModuleHandleA
        f.argtypes = (c_char_p,)
        f.restype = NoNullHandle

        strchr = cdll.msvcrt.strchr
        strchr.restype = c_char_p
        strchr.argtypes = (c_char_p, c_char)
        self.failUnless(strchr("abcdefghi", "b") == "bcdefghi")
        self.failUnless(strchr("abcdefghi", "x") == None)

        strtok = cdll.msvcrt.strtok
        strtok.restype = c_char_p
        # Neither of this does work
##        strtok.argtypes = (c_char_p, c_char_p)
##        strtok.argtypes = (c_string, c_char_p)

        s = "a\nb\nc"

        b = c_string(s)
        self.failUnless(strtok(b, "\n") == "a")
        self.failUnless(strtok(None, "\n") == "b")
        self.failUnless(strtok(None, "\n") == "c")
        self.failUnless(strtok(None, "\n") == None)
        
def get_suite():
    return unittest.makeSuite(CFuncPtrTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
