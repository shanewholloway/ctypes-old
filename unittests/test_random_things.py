from ctypes import *
import unittest

def __del__(self):
    pass

class MyTestCase(unittest.TestCase):
    def test_comcrash(self):
        from ctypes.com import IUnknown
        p = pointer(IUnknown())
        # We replace the __del__ method (which calls self.Release(),
        # because it would crash.
        POINTER(IUnknown).__del__ = __del__
        try:
            p.AddRef()
        except ValueError, message:
            self.failUnlessEqual(str(message), "COM method call without VTable")
        else:
            self.fail("Exception expected")

def get_suite():
    import os
    if os.name == "nt":
        return unittest.makeSuite(MyTestCase)
    else:
        return None

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    test()
