import unittest
import ctypes
import gc

MyCallback = ctypes.CALLBACK(ctypes.c_int, ctypes.c_int)
OtherCallback = ctypes.CALLBACK(ctypes.c_int, ctypes.c_int, ctypes.c_ulonglong)

class RefcountTestCase(unittest.TestCase):
    def setUp(self):
        global dll
        from ctypes import _ctypes
        dll = ctypes.CDLL(_ctypes.__file__)

    def test_1(self):
        from sys import getrefcount as grc

        f = dll._testfunc_callback_i_if
        f.restype = ctypes.c_int
        f.argtypes = [ctypes.c_int, MyCallback]

        def callback(value):
            #print "called back with", value
            return value

        self.failUnless(grc(callback) == 2)
        cb = MyCallback(callback)

        self.failUnless(grc(callback) > 2)
        result = f(-10, cb)
        self.failUnless(result == -18)
        cb = None

        gc.collect()

        self.failUnless(grc(callback) == 2)


    def test_refcount(self):
        from sys import getrefcount as grc
        def func(*args):
            pass
        # this is the standard refcount for func
        self.failUnless(grc(func) == 2)

        # the CFuncPtr instance holds atr least one refcount on func:
        f = OtherCallback(func)
        self.failUnless(grc(func) > 2)

        # and may release it again
        del f
        self.failUnless(grc(func) >= 2)
        
        # but now it must be gone
        gc.collect()
        self.failUnless(grc(func) == 2)

        class X(ctypes.Structure):
            _fields_ = [("a", OtherCallback)]
        x = X()
        x.a = OtherCallback(func)
        
        # the CFuncPtr instance holds atr least one refcount on func:
        self.failUnless(grc(func) > 2)

        # and may release it again
        del x
        self.failUnless(grc(func) >= 2)
        
        # and now it must be gone again
        gc.collect()
        self.failUnless(grc(func) == 2)

        f = OtherCallback(func)

        # the CFuncPtr instance holds atr least one refcount on func:
        self.failUnless(grc(func) > 2)

        # create a cycle
        f.cycle = f

        del f
        gc.collect()
        self.failUnless(grc(func) == 2)
        

def get_suite():
    return unittest.makeSuite(RefcountTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
