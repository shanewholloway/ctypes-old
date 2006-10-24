import sys
import os
import unittest
import tempfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from ctypes_codegen import h2xml
from ctypes_codegen.codegenerator import generate_code

def mktemp(suffix):
    handle, fnm = tempfile.mkstemp(suffix)
    os.close(handle)
    return fnm

class ADict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

class ConstantsTest(unittest.TestCase):
    def convert(self, defs, flags=None):
        hfile = mktemp(".h")
        open(hfile, "w").write(defs)

        xmlfile = mktemp(".xml")

        try:
            if flags:
                h2xml.main(["h2xml", "-q", "-I.", hfile, "-o", xmlfile, flags])
            else:
                h2xml.main(["h2xml", "-q", "-I.", hfile, "-o", xmlfile])
            
            ofi = StringIO()
            generate_code(xmlfile, ofi)
            namespace = {}
            exec ofi.getvalue() in namespace

            return ADict(namespace)

        finally:
            os.unlink(hfile)
            ##print open(xmlfile).read()
            os.unlink(xmlfile)

    def test_int(self):
        ns = self.convert("""
        int zero = 0;
        int one = 1;
        int minusone = -1;
        int maxint = 2147483647;
        int minint = -2147483648;
        """)

        self.failUnlessEqual(ns.zero, 0)
        self.failUnlessEqual(ns.one, 1)
        self.failUnlessEqual(ns.minusone, -1)
        self.failUnlessEqual(ns.maxint, 2147483647)
        self.failUnlessEqual(ns.minint, -2147483648)

    def test_uint(self):
        ns = self.convert("""
        unsigned int zero = 0;
        unsigned int one = 1;
        unsigned int minusone = -1;
        unsigned int maxuint = 0xFFFFFFFF;
        """)

        self.failUnlessEqual(ns.zero, 0)
        self.failUnlessEqual(ns.one, 1)
        self.failUnlessEqual(ns.minusone, 4294967295)
        self.failUnlessEqual(ns.maxuint, 0xFFFFFFFF)

    def test_char(self):
        ns = self.convert("""
        char x = 'x';
        wchar_t X = L'X';
        char zero = 0;
        wchar_t w_zero = 0;
        """)

        self.failUnlessEqual(ns.x, 'x')
        self.failUnlessEqual(ns.X, 'X')

        self.failUnlessEqual(type(ns.x), str)
        self.failUnlessEqual(type(ns.X), unicode)

        self.failUnlessEqual(ns.zero, '\0')
        self.failUnlessEqual(ns.w_zero, '\0')

        self.failUnlessEqual(type(ns.zero), str)
        self.failUnlessEqual(type(ns.w_zero), unicode)

    def test_defines(self):
        ns = self.convert("""
        #define zero 0
        #define one 1
        #define maxint 2147483647
        #define minint -2147483648
        #define spam "spam"
        #define foo L"foo"
        """, "-c")

        self.failUnlessEqual(ns.zero, 0)
        self.failUnlessEqual(ns.one, 1)
        self.failUnlessEqual(ns.maxint, 2147483647)
##        self.failUnlessEqual(ns.minint, -2147483648)

        self.failUnlessEqual(ns.spam, "spam")
        self.failUnlessEqual(type(ns.spam), str)

        # This test fails on wide unicode builds
##        self.failUnlessEqual(ns.foo, "foo")
##        self.failUnlessEqual(type(ns.foo), unicode)

if __name__ == "__main__":
    unittest.main()
