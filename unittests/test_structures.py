import unittest
from ctypes import *
from struct import calcsize
from _ctypes import alignment

class StructureTestCase(unittest.TestCase):
    formats = "csbBhHiIlLqQdf"

    def test_simple_structs(self):
        for code in self.formats:
            class X(Structure):
                _fields_ = [("x", "c"),
                            ("y", code)]
            self.failUnless(sizeof(X) == calcsize("c%c0%c" % (code, code)))

    def test_unions(self):
        for code in self.formats:
            class X(Union):
                _fields_ = [("x", "c"),
                            ("y", code)]
            self.failUnless(sizeof(X) == calcsize("%c" % (code)))

    def test_struct_alignment(self):
        print
        class X(Structure):
            _fields_ = [("x", "3s")]
        self.failUnless(alignment(X) == calcsize("s"))
        self.failUnless(sizeof(X) == calcsize("3s"))

        class Y(Structure):
            _fields_ = [("x", "3s"),
                        ("y", "i")]
        self.failUnless(alignment(Y) == calcsize("i"))
        self.failUnless(sizeof(Y) == calcsize("3si"))

        class SI(Structure):
            _fields_ = [("a", X),
                        ("b", Y)]
        self.failUnless(alignment(SI) == max(alignment(Y), alignment(X)))
        self.failUnless(sizeof(SI) == calcsize("3s0i 3si 0i"))
        
        class IS(Structure):
            _fields_ = [("b", Y),
                        ("a", X)]

        self.failUnless(alignment(SI) == max(alignment(X), alignment(Y)))
        self.failUnless(sizeof(IS) == calcsize("3si 3s 0i"))

        class XX(Structure):
            _fields_ = [("a", X),
                        ("b", X)]
        self.failUnless(alignment(XX) == alignment(X))
        self.failUnless(sizeof(XX) == calcsize("3s 3s 0s"))

    def test_emtpy(self):
        # I had problems with these
        #
        # Although these are patological cases: Empty Structures!
        class X(Structure):
            _fields_ = []

        class Y(Union):
            _fields_ = []

        # Is this really the correct alignment, or should it be 0?
        self.failUnless(alignment(X) == alignment(Y) == 1)
        self.failUnless(sizeof(X) == sizeof(Y) == 0)

        class XX(Structure):
            _fields_ = [("a", X),
                        ("b", X)]

        self.failUnless(alignment(XX) == 1)
        self.failUnless(sizeof(XX) == 0)


def get_suite():
    return unittest.makeSuite(StructureTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()

