import unittest
from ctypes import windll, POINTER, byref
from comtypes import IUnknown

class BasicTest(unittest.TestCase):
    def test_IUnknown(self):
        from comtypes import IUnknown
        self.failUnlessEqual(IUnknown._nummethods_, 3)

    def test_release(self):
        POINTER(IUnknown)()

    def test_refcounts(self):
        p = POINTER(IUnknown)()
        windll.oleaut32.CreateTypeLib(1, u"blabla", byref(p))
        # initial refcount is 2
        for i in range(2, 10):
            self.failUnlessEqual(p.AddRef(), i)
        for i in range(8, 0, -1):
            self.failUnlessEqual(p.Release(), i)

    def test_qi(self):
        p = POINTER(IUnknown)()
        windll.oleaut32.CreateTypeLib(1, u"blabla", byref(p))
        self.failUnlessEqual(p.AddRef(), 2)
        self.failUnlessEqual(p.Release(), 1)

        other = p.QueryInterface(IUnknown)
        self.failUnlessEqual(other.AddRef(), 3)
        self.failUnlessEqual(p.AddRef(), 4)
        self.failUnlessEqual(p.Release(), 3)
        self.failUnlessEqual(other.Release(), 2)

        del p # calls p.Release()

        self.failUnlessEqual(other.AddRef(), 2)
        self.failUnlessEqual(other.Release(), 1)
        
    def test_derived(self):

        class IMyInterface(IUnknown):
            pass

        self.failUnlessEqual(IMyInterface._nummethods_, 3)

        IMyInterface._methods_ = []
        self.failUnlessEqual(IMyInterface._nummethods_, 3)

    def test_mro(self):
        mro = POINTER(IUnknown).__mro__

        self.failUnlessEqual(mro[0], POINTER(IUnknown))
        self.failUnlessEqual(mro[1], IUnknown)

        # the IUnknown class has the actual methods:
        self.failUnless(IUnknown.__dict__.get("QueryInterface"))

if __name__ == "__main__":
    unittest.main()
