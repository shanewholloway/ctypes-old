import unittest
import ctypes

class MyCallback(ctypes.CFunction):
    _stdcall_ = 0
    _types_ = ctypes.c_int,


class RefcountTestCase(unittest.TestCase):
    def setUp(self):
        global dll
        import _ctypes
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
        self.failUnless(grc(callback) == 3)
        result = f(-10, cb)
        self.failUnless(result == -18)
        cb = None
        self.failUnless(grc(callback) == 2)


def get_suite():
    return unittest.makeSuite(RefcountTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
