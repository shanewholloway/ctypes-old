import unittest
import os
from ctypes_codegen import h2xml
from ctypes_codegen.codegenerator import generate_code
import tempfile
from cStringIO import StringIO

os.environ["GCCXML_COMPILER"] = "msvc71"

INCLUDE = """
int i = -1;
unsigned int ui = -1;
__int64 i64 = -1;

/*
unsigned __int64 ui64 = -1;
*/
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
            self.failUnlessEqual(namespace["i64"], -1)

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
