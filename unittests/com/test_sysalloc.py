import unittest
from ctypes import *
from ctypes.com import mallocspy, ole32
# We init COM before each test, and uninit afterwards
ole32.CoUninitialize()


class BSTRTest(unittest.TestCase):
    def setUp(self):
        self.mallocspy = mallocspy.MallocSpy()
        self.mallocspy.register()

    def tearDown(self):
        self.mallocspy.revoke(warn=0)

    ################

    def test_leak(self):
        ole32.CoInitialize(None)

        # Allocate 10 BSTR's without freeing them, and make sure the
        # leak is detected
        for i in range(10):
            windll.oleaut32.SysAllocString(unicode("Python is cool"))
        ole32.CoUninitialize()

        self.failUnlessEqual(len(self.mallocspy.active_blocks()), 10)

    def test_noleak(self):
        ole32.CoInitialize(None)

        # Allocate 10 BSTR's then free them, and make sure *no* leak
        # is detected
        L = []
        for i in range(10):
            b = windll.oleaut32.SysAllocString(unicode("Python is cool"))
            L.append(b)

        for b in L:
            windll.oleaut32.SysFreeString(b)
        ole32.CoUninitialize()

        self.failUnlessEqual(self.mallocspy.active_blocks(), {})
        
################################################################

if __name__ == "__main__":
    unittest.main()
        
