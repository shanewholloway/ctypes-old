import unittest, sys, gc
from ctypes import *

class LeakTestCase(unittest.TestCase):

    ################

    def make_noncyclic_structures(self, repeat):
        for i in xrange(repeat):
            class POINT(Structure):
                _fields_ = [("x", c_int), ("y", c_int)]
            class RECT(Structure):
                _fields_ = [("ul", POINT),
                            ("br", POINT)]

    if not hasattr(sys, "gettotalrefcount"):
        print >> sys.stderr, "(can only test for refcount leaks in debug build!)"
    else:

        def test_no_cycles_refcount(self):
            last_refcount = 0
            for x in xrange(20):
                self.make_noncyclic_structures(1000)
                while gc.collect():
                    pass
                total_refcount = sys.gettotalrefcount()
                if last_refcount >= total_refcount:
                    return # test passed
                last_refcount = total_refcount
            self.fail("it seems the total refcounts grows without bounds")

    def test_no_cycles_objcount(self):
        last_objcount = 0
        for x in xrange(20):
            self.make_noncyclic_structures(1000)
            while gc.collect():
                pass
            total_objcount = gc.get_objects()
            if last_objcount >= total_objcount:
                return # test passed
            last_objcount = total_objcount
        self.fail("it seems the number of objects grows without bounds")

    ################

    def make_cyclic_structures(self, repeat):
        for i in xrange(repeat):
            class LIST(Structure):
                pass

            LIST._fields_ = [("pnext", POINTER(LIST))]

    if hasattr(sys, "gettotalrefcount"):

        def test_cycles_refcount(self):
            last_refcount = 0
            for x in xrange(5):
                self.make_cyclic_structures(1000)
                while gc.collect():
                    pass
                total_refcount = sys.gettotalrefcount()
                if last_refcount >= total_refcount:
                    return
                last_refcount = total_refcount
            self.fail("it seems the total refcounts grows without bounds")

    def test_cycles_objcount(self):
        last_objcount = 0
        for x in xrange(5):
            self.make_cyclic_structures(1000)
            while gc.collect():
                pass
            total_objcount = len(gc.get_objects())
            if last_objcount >= total_objcount:
                return
            last_objcount = total_objcount
        self.fail("it seems the number of objects grows without bounds")

if __name__ == "__main__":
    unittest.main()