import glob
import os
import unittest
import comtypes.typeinfo
import comtypes.client
import comtypes.client._generate
# don't print messages when typelib wrappers are generated
comtypes.client._generate.__verbose__ = False

sysdir = os.path.join(os.environ["SystemRoot"], "system32")

# This test takes quite some time.  It tries to build wrappers for ALL
# .dll, .tlb, and .ocx files in the system directory which contain typelibs.
import ctypes.test
ctypes.test.requires("typelibs")


class Test(unittest.TestCase):
    def setUp(self):
        comtypes.client.gen_dir = None

    def tearDown(self):
        comtypes.client.gen_dir = comtypes.client._find_gen_dir()
    
number = 0

def add_test(fname):
    global number
    try:
        comtypes.typeinfo.LoadTypeLibEx(fname)
    except WindowsError:
        return
    def test(self):
        comtypes.client.GetModule(fname)

    test.__doc__ = "test GetModule(%r)" % fname
    setattr(Test, "test_%d" % number, test)
    number += 1

for fname in glob.glob(os.path.join(sysdir, "*.ocx")):
    add_test(fname)

for fname in glob.glob(os.path.join(sysdir, "*.tlb")):
    add_test(fname)

for fname in glob.glob(os.path.join(sysdir, "*.dll")):
    add_test(fname)

if __name__ == "__main__":
    unittest.main()