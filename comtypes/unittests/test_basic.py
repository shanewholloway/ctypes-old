import unittest
from ctypes import windll, POINTER, byref, HRESULT
from comtypes import IUnknown, STDMETHOD

def method_count(interface):
    return sum([len(base.__dict__.get("_methods_", ()))
                for base in interface.__mro__])

class BasicTest(unittest.TestCase):
    def test_IUnknown(self):
        from comtypes import IUnknown
        self.failUnlessEqual(method_count(IUnknown), 3)

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

        self.failUnlessEqual(method_count(IUnknown), 3)

        class IMyInterface(IUnknown):
            pass

        self.failUnlessEqual(method_count(IMyInterface), 3)

        IMyInterface._methods_ = []
        self.failUnlessEqual(method_count(IMyInterface), 3)

        IMyInterface._methods_ = [
            STDMETHOD(HRESULT, "Blah", [])]
        self.failUnlessEqual(method_count(IMyInterface), 4)

    def test_mro(self):
        mro = POINTER(IUnknown).__mro__

        self.failUnlessEqual(mro[0], POINTER(IUnknown))
        self.failUnlessEqual(mro[1], IUnknown)

        # the IUnknown class has the actual methods:
        self.failUnless(IUnknown.__dict__.get("QueryInterface"))

##    def test_identity(self):
##        p = POINTER(IUnknown)()
####        p[0]
##        windll.oleaut32.CreateTypeLib(1, u"blabla", byref(p))

##        p = p.QueryInterface(IUnknown)
##        other = p.QueryInterface(IUnknown)

##        print other == p
##        print other is p
##        print "A"
##        print "?", p[0]
##        print "B"
####        p[0] = 42
##        print "C"
##        print dir(p)
##        from ctypes import cast, c_int
##        print cast(other, c_int).value
##        print cast(p, c_int).value

##        x = POINTER(IUnknown)()
##        windll.oleaut32.CreateTypeLib(1, u"blabla_2", byref(x))
##        x = x.QueryInterface(IUnknown)

##        print cast(x, c_int).value

##        print "D"
##        del p
##        print "E"
##        del other
##        print "F"

if __name__ == "__main__":
    unittest.main()
