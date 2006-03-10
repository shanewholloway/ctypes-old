from ctypes import *
import sys, unittest
import os, StringIO

class LoaderTest(unittest.TestCase):

    unknowndll = "xxrandomnamexx"

    def test_load(self):
        if os.name == "nt":
            name = "msvcrt"
        elif os.name == "ce":
            name = "coredll"
        elif sys.platform == "darwin":
            name = "libc.dylib"
        elif sys.platform.startswith("freebsd"):
            name = "libc.so"
        elif sys.platform == "sunos5":
            name = "libc.so"
        else:
            name = "libc.so.6"
        cdll.load(name)
        self.assertRaises(OSError, cdll.load, self.unknowndll)

    def test_load_version(self):
        version = "6"
        name = "c"
        if sys.platform == "linux2":
            cdll.load_version(name, version)
            # linux uses version, libc 9 should not exist
            self.assertRaises(OSError, cdll.load_version, name, "9")
        self.assertRaises(OSError, cdll.load_version, self.unknowndll, "")

    if os.name == "posix" and sys.platform != "sunos5":
        def test_find(self):
            name = "c"
            cdll.find(name)
            self.assertRaises(OSError, cdll.find, self.unknowndll)

    def test_load_library(self):
        if os.name in ("nt", "ce"):
            windll.load_library("kernel32").GetModuleHandleW
            windll.LoadLibrary("kernel32").GetModuleHandleW
            WinDLL("kernel32").GetModuleHandleW

    def XXX_test_load_ordinal_functions(self):
        # Not yet
        pass

if __name__ == "__main__":
    unittest.main()
