import unittest, os
from ctypes import *

def get_refcnt(comptr):
    if not comptr:
        return 0
    comptr.AddRef()
    return comptr.Release()

class ComTestCase(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        global COMObject, IUnknown, GUID
        from ctypes.com import COMObject, IUnknown, GUID

    def setUp(self):
        class Factory(object):
            def LockServer(self, *args):
                pass

        class MyObject(COMObject):
            _factory = Factory()
            _com_interfaces_ = [IUnknown]

        self.impl = MyObject()

    def tearDown(self):
        self.impl = None

    ################

    def test_comobject(self):
        impl = self.impl
        self.failUnlessEqual(impl._refcnt, 0)
        p = pointer(impl._com_pointers_[0][1])
        p.AddRef()
        self.failUnlessEqual(impl._refcnt, 1)
        self.failUnlessEqual(get_refcnt(p), 1)
        del p
        self.failUnlessEqual(impl._refcnt, 0)

    def test_qi(self):
        impl = self.impl
        self.failUnlessEqual(impl._refcnt, 0)
        p = pointer(impl._com_pointers_[0][1])
        p.AddRef()

        self.failUnlessEqual(get_refcnt(p), 1)

        p2 = POINTER(IUnknown)()
        p.QueryInterface(byref(IUnknown._iid_), byref(p2))
        self.failUnlessEqual(get_refcnt(p), 2)

    def test_from_progid(self):
        g = GUID.from_progid("InternetExplorer.Application")
        self.failUnlessEqual(g, GUID("{0002DF01-0000-0000-C000-000000000046}"))

    def test_GUID(self):
        g1 = GUID("{00000000-0001-0002-0003-000000000000}")
        g2 = GUID("{00000000-0001-0002-0003-000000000000}")
        g3 = GUID("{00000000-0001-0002-0003-000000000001}")
        self.failUnlessEqual(g1, g2)
        # for now, GUID instances are unhashable.
##        d = {}
##        d[g1] = None
##        self.failUnlessEqual(g1 in d, True)
##        self.failUnlessEqual(g2 in d, True)
##        self.failUnlessEqual(g3 in d, False)

################################################################

def get_suite():
    if os.name == "nt":
        return unittest.makeSuite(ComTestCase)
    return None

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
