import unittest, os
from ctypes import *

def get_refcnt(comptr):
    # return the COM reference count of a COM interface pointer
    if not comptr:
        return 0
    comptr.AddRef()
    return comptr.Release()

if os.name == "nt":
    class VariantTestCase(unittest.TestCase):

        def __init__(self, *args):
            # We cannot import these at module level, but want these to be
            # available in the global namespace
            global IUnknown, VARIANT, LoadTypeLibEx, DISPPARAMS, LoadRegTypeLib, GUID
            from ctypes.com import IUnknown, GUID
            from ctypes.com.automation import VARIANT, LoadTypeLibEx, DISPPARAMS, LoadRegTypeLib
            unittest.TestCase.__init__(self, *args)

        def test_com_refcounts(self):
            # typelib for Internet Explorer
            tlb = LoadRegTypeLib(GUID("{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}"), 1, 1, 0)
            self.failUnlessEqual(get_refcnt(tlb), 1)

            p = POINTER(IUnknown)()
            tlb.QueryInterface(byref(IUnknown._iid_), byref(p))
            self.failUnlessEqual(get_refcnt(tlb), 2)

            del p
            self.failUnlessEqual(get_refcnt(tlb), 1)


        def test_com_pointers(self):
##            """Storing a COM interface pointer in a VARIANT increments the refcount,
##            changing the variant to contain something else decrements it"""
            tlb = LoadRegTypeLib(GUID("{EAB22AC0-30C1-11CF-A7EB-0000C05BAE0B}"), 1, 1, 0)
            self.failUnlessEqual(get_refcnt(tlb), 1)

            v = VARIANT(tlb)
            self.failUnlessEqual(get_refcnt(tlb), 2)

            p = v.value
            self.failUnlessEqual(get_refcnt(tlb), 3)
            del p
            self.failUnlessEqual(get_refcnt(tlb), 2)

            v.value = None
            self.failUnlessEqual(get_refcnt(tlb), 1)


        def test_null_com_pointers(self):
            p = POINTER(IUnknown)()
            self.failUnlessEqual(get_refcnt(p), 0)

            v = VARIANT(p)
            self.failUnlessEqual(get_refcnt(p), 0)

        def test_dispparams(self):
            # DISPPARAMS is a complex structure, well worth testing.
            d = DISPPARAMS()
            d.rgvarg = (VARIANT * 3)()
            # XXX The following line fails, which is a real bug in ctypes:
            # SystemError: ...\Objects\listobject.c:105: bad argument to internal function
    ##        d.rgvarg[0].value = 1

        def test_pythonobjects(self):
            objects = [None, 42, 3.14, True, False, "abc", u"abc"]
            for x in objects:
                v = VARIANT(x)
                self.failUnlessEqual(x, v.value)

################################################################

if __name__ == '__main__':
    unittest.main()
