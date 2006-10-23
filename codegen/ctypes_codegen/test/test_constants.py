import unittest
import os
from ctypes_codegen import h2xml
from ctypes_codegen.codegenerator import generate_code
import tempfile
from cStringIO import StringIO

INCLUDE = """
int i = -1;
unsigned int ui = -1;

#ifdef _MSC_VER
__int64 i64 = -1;
#else
long long int i64 = 0x12345678ABCDEF;
#endif
"""

class ConstantsTest(unittest.TestCase):
    def test(self):
        handle, hfile = tempfile.mkstemp(".h")
        os.close(handle)
        open(hfile, "w").write(INCLUDE)

        handle, xmlfile = tempfile.mkstemp(".xml")
        os.close(handle)

        try:
            h2xml.main(["h2xml", "-q", "-I.", hfile, "-o", xmlfile])
            
            ofi = StringIO()
            generate_code(xmlfile, ofi)
            namespace = {}
            exec ofi.getvalue() in namespace

            self.failUnlessEqual(namespace["i"], -1)
            self.failUnlessEqual(namespace["ui"], 0xFFFFFFFF)

        finally:
            print "Remove", hfile
            os.unlink(hfile)
            print "Remove", xmlfile
            os.unlink(xmlfile)

"""
def generate_code(xmlfile,
                  outfile,
                  expressions=None,
                  symbols=None,
                  verbose=False,
                  generate_comments=False,
                  known_symbols=None,
                  searched_dlls=None,
                  types=None):
"""

if __name__ == "__main__":
    unittest.main()
