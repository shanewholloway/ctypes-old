import unittest, os, sys
from ctypes import *

def get_refcnt(comptr):
    if not comptr:
        return 0
    comptr.AddRef()
    return comptr.Release()


class Test_EmptyComPointer(unittest.TestCase):
    # This test makes sure that calling a COM method on a COM
    # interface pointer raises a ValueError, when the interface
    # pointer points to NULL.

    def setUp(self):
        from ctypes.com import IUnknown
        self._orig_del = POINTER(IUnknown).__del__
        # We replace the __del__ method (which calls self.Release(),
        # because it would crash.
        def __del__(self):
            pass
        POINTER(IUnknown).__del__ = __del__

    def tearDown(self):
        from ctypes.com import IUnknown
        POINTER(IUnknown).__del__ = self._orig_del

    def test_comcrash(self):
        from ctypes.com import IUnknown
        p = pointer(IUnknown())
        try:
            p.AddRef()
        except ValueError, message:
            self.failUnlessEqual(str(message), "COM method call without VTable")
        else:
            self.fail("Exception expected")

class ComTestCase(unittest.TestCase):
    def __init__(self, *args):
        unittest.TestCase.__init__(self, *args)
        global COMObject, IUnknown, GUID, STDMETHOD, HRESULT
        from ctypes.com import COMObject, IUnknown, GUID, STDMETHOD, HRESULT

    def setUp(self):
        class IObjectWithSite(IUnknown):
            _iid_ = GUID("{FC4801A3-2BA9-11CF-A229-00AA003D7352}")
            _methods_ = IUnknown._methods_ + [ 
                (STDMETHOD(HRESULT, "SetSite", POINTER(IUnknown))),
                (STDMETHOD(HRESULT, "GetSite", POINTER(GUID), POINTER(c_void_p)))]

        class Factory(object):
            def LockServer(self, *args):
                pass

        class MyObject(COMObject):
            _factory = Factory()
            _com_interfaces_ = [IObjectWithSite]

            def IObjectWithSite_SetSite(self, this, pUnkSite):
                self.m_site = pUnkSite
                return 0 # S_OK

        self.impl = MyObject()

    def tearDown(self):
        self.impl = None
        import gc
        gc.collect()

    ################

    def test_site(self):
        impl = self.impl
        p = pointer(impl._com_pointers_[0][1])
        self.failUnlessEqual(impl._refcnt, 0)
        p.AddRef()
        self.failUnlessEqual(impl._refcnt, 1)
        p.SetSite(p)
        self.failUnlessEqual(impl._refcnt, 2)
        p.SetSite(None)
        self.failUnlessEqual(impl._refcnt, 1)
        del p
        self.failUnlessEqual(impl._refcnt, 0)

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
        del p2
        self.failUnlessEqual(get_refcnt(p), 1)

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

if __name__ == '__main__':
    unittest.main()
