import unittest
from ctypes import * # bad style, generally

try:
    WINFUNCTYPE
except NameError:
    # fake to enable this test on Linux
    WINFUNCTYPE = CFUNCTYPE

import os, sys
if os.name == "nt":
    libc = cdll.msvcrt
    
elif os.name == "posix":
    if sys.platform == "darwin":
        libc = cdll.LoadLibrary("/usr/lib/libc.dylib")
    else:
        libc = cdll.LoadLibrary("/lib/libc.so.6")

class CFuncPtrTestCase(unittest.TestCase):
    def test_basic(self):
        X = WINFUNCTYPE(c_int, c_int, c_int)

        def func(*args):
            return len(args)

        x = X(func)
        self.failUnlessEqual(x.restype, c_int)
        self.failUnlessEqual(x.argtypes, (c_int, c_int))
        self.failUnlessEqual(sizeof(x), sizeof(c_voidp))
        self.failUnlessEqual(sizeof(X), sizeof(c_voidp))

    def test_first(self):
        StdCallback = WINFUNCTYPE(c_int, c_int, c_int)
        CdeclCallback = CFUNCTYPE(c_int, c_int, c_int)

        def func(a, b):
            return a + b

        s = StdCallback(func)
        c = CdeclCallback(func)

        self.failUnless(s(1, 2) == 3)
        self.failUnless(c(1, 2) == 3)
        self.assertRaises(TypeError, s, 1, 2, 3)
        self.assertRaises(TypeError, c, 1, 2, 3)

    def test_structures(self):
        WNDPROC = WINFUNCTYPE(c_long, c_int, c_int, c_int, c_int)

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

        WNDPROC_2 = WINFUNCTYPE(c_long, c_int, c_int, c_int, c_int)

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

##        f = windll.kernel32.GetModuleHandleA
##        f.argtypes = (c_char_p,)
##        f.restype = NoNullHandle

        strchr = libc.strchr
        strchr.restype = c_char_p
        strchr.argtypes = (c_char_p, c_char)
        self.failUnless(strchr("abcdefghi", "b") == "bcdefghi")
        self.failUnless(strchr("abcdefghi", "x") == None)

        strtok = libc.strtok
        strtok.restype = c_char_p
        # Neither of this does work
##        strtok.argtypes = (c_char_p, c_char_p)
##        strtok.argtypes = (c_string, c_char_p)

        def c_string(init):
            size = len(init) + 1
            return (c_char*size)(*init)

        s = "a\nb\nc"
        b = c_string(s)

##        b = (c_char * (len(s)+1))()
##        b.value = s

##        b = c_string(s)
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
