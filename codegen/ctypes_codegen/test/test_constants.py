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
    def convert(self, defs):
        handle, hfile = tempfile.mkstemp(".h")
        os.close(handle)
        open(hfile, "w").write(defs)

        handle, xmlfile = tempfile.mkstemp(".xml")
        os.close(handle)

        try:
            h2xml.main(["h2xml", "-q", "-I.", hfile, "-o", xmlfile])
            
            ofi = StringIO()
            generate_code(xmlfile, ofi)
            namespace = {}
            exec ofi.getvalue() in namespace

            return namespace

        finally:
            os.unlink(hfile)
            os.unlink(xmlfile)

    def test_int(self):
        ns = self.convert("""
        int zero = 0;
        int one = 1;
        int minusone = -1;
        int maxint = 2147483647;
        int minint = -2147483648;
        """)
        self.failUnlessEqual(ns["zero"], 0)
        self.failUnlessEqual(ns["one"], 1)
        self.failUnlessEqual(ns["minusone"], -1)
        self.failUnlessEqual(ns["maxint"], 2147483647)
        self.failUnlessEqual(ns["minint"], -2147483648)

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
