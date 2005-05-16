from ctypes import *
import unittest
import os, StringIO

class LoaderTest(unittest.TestCase):

    unknowndll = "xxrandomnamexx"

    def test_LoadLibrary(self):
	if os.name == "nt":
	    name = "msvcrt"
	elif sys.platform == "darwin":
	    name = "libc.dylib"
	else:
	    name = "libc.so.6"
	cdll.LoadLibrary(name)
	self.assertRaises(OSError, cdll.LoadLibrary, self.unknowndll)

    def test_LoadLibraryVersion(self):
	version = "6"
        name = "c"
	cdll.LoadLibraryVersion(name, version)
	if sys.platform == "linux2":
	    # linux uses version, libc 9 should not exist
	    self.assertRaises(OSError, cdll.LoadLibraryVersion, name, "9")
	self.assertRaises(OSError, cdll.LoadLibraryVersion, self.unknowndll, "")

    def test_find(self):
        name = "c"
        cdll.find(name, False)
	self.assertRaises(OSError, cdll.find, self.unknowndll)

if __name__ == "__main__":
    unittest.main()
