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

    def test_dllfunctions(self):
        class WINAPI(CFuncPtr):
            _restype_ = c_int
            _flags_ = FUNCFLAG_STDCALL

        class STDAPI(CFuncPtr):
            _restype_ = c_int
            _flags_ = FUNCFLAG_CDECL
            
        def NoNullHandle(value):
            if not value:
                raise WinError()
            return value

        f = WINAPI("GetModuleHandleA", windll.kernel32)
        f.argtypes = (c_char_p,)
        f.restype = NoNullHandle

        import sys
        self.failUnless(f("python22") == sys.dllhandle)

        strchr = STDAPI("strchr", cdll.msvcrt)
        strchr.restype = c_char_p
        strchr.argtypes = (c_char_p, c_char)
        self.failUnless(strchr("abcdefghi", "b") == "bcdefghi")
        self.failUnless(strchr("abcdefghi", "x") == None)

        strtok = STDAPI("strtok", cdll.msvcrt)
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
