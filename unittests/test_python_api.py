from ctypes import *
import unittest, sys

################################################################
# This section should be moved into ctypes\__init__.py, when it's ready.

from _ctypes import PyObj_FromPtr

from _ctypes import _SimpleCData
class PyObject(_SimpleCData):
    _type_ = "O"

if sys.platform == "win32":
    python = getattr(pydll, "python%s%s" % sys.version_info[:2])
else:
    python = PyDLL(None)

################################################################

from sys import getrefcount as grc


class PythonAPITestCase(unittest.TestCase):

    def test_PyString_FromString(self):
        python.PyString_FromString.restype = PyObject
        python.PyString_FromString.argtypes = (c_char_p,)

        s = "abc"
        refcnt = grc(s)
        pyob = python.PyString_FromString(s)
        self.failUnlessEqual(grc(s), refcnt)
        self.failUnlessEqual(s, pyob)
        del pyob
        self.failUnlessEqual(grc(s), refcnt)

    def test_PyInt_Long(self):
        ref42 = grc(42)
        python.PyInt_FromLong.restype = PyObject
        self.failUnlessEqual(python.PyInt_FromLong(42), 42)

        self.failUnlessEqual(grc(42), ref42)

        python.PyInt_AsLong.argtypes = (PyObject,)
        python.PyInt_AsLong.restype = c_int

        res = python.PyInt_AsLong(42)
        self.failUnlessEqual(grc(res), ref42 + 1)
        del res
        self.failUnlessEqual(grc(42), ref42)

    def test_PyObj_FromPtr(self):
        s = "abc def ghi jkl"
        ref = grc(s)
        # id(python-object) is the address
        pyobj = PyObj_FromPtr(id(s))
        self.failUnless(s is pyobj)

        self.failUnlessEqual(grc(s), ref + 1)
        del pyobj
        self.failUnlessEqual(grc(s), ref)

if __name__ == "__main__":
    unittest.main()
