import unittest
from ctypes import * # bad style, generally

try:
    WINFUNCTYPE
except NameError:
    # fake to enable this test on Linux
    WINFUNCTYPE = CFUNCTYPE


def get_libc():
    import os, sys
    if os.name == "nt":
        return cdll.msvcrt
    elif os.name == "posix":
        if sys.platform == "darwin":
            return cdll.LoadLibrary("/usr/lib/libc.dylib")
        elif sys.platform == "cygwin":
            return cdll.LoadLibrary("/bin/cygwin1.dll")
        elif sys.platform == "sunos5":
            return cdll.LoadLibrary("/lib/libc.so")
        else:
            try:
                return cdll.LoadLibrary("/lib/libc.so.6")
            except OSError:
                pass
    return None
libc = get_libc()

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

        self.failUnlessEqual(s(1, 2), 3)
        self.failUnlessEqual(c(1, 2), 3)
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

        # This is no longer true, now that WINFUNCTYPE caches created types internally.
        ## # CFuncPtr subclasses are compared by identity, so this raises a TypeError:
        ## self.assertRaises(TypeError, setattr, wndclass,
        ##                  "lpfnWndProc", WNDPROC_2(wndproc))
        # instead:

        self.failUnless(WNDPROC is WNDPROC_2)
        self.failUnlessEqual(wndclass.lpfnWndProc(1, 2, 3, 4), 10)

        f = wndclass.lpfnWndProc

        del wndclass
        del wndproc

        self.failUnlessEqual(f(10, 11, 12, 13), 46)

    if libc is not None:
        def test_dllfunctions(self):

            def NoNullHandle(value):
                if not value:
                    raise WinError()
                return value

            strchr = libc.strchr
            strchr.restype = c_char_p
            strchr.argtypes = (c_char_p, c_char)
            self.failUnlessEqual(strchr("abcdefghi", "b"), "bcdefghi")
            self.failUnlessEqual(strchr("abcdefghi", "x"), None)

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
            self.failUnlessEqual(strtok(b, "\n"), "a")
            self.failUnlessEqual(strtok(None, "\n"), "b")
            self.failUnlessEqual(strtok(None, "\n"), "c")
            self.failUnlessEqual(strtok(None, "\n"), None)
        
if __name__ == '__main__':
    unittest.main()
