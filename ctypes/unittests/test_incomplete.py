import unittest
from ctypes import *

################################################################
#
# The incomplete pointer example from the tutorial
#

class MyTestCase(unittest.TestCase):

    def test_incomplete_example(self):
        lpcell = POINTER("cell")
        class cell(Structure):
            _fields_ = [("name", c_char_p),
                        ("next", lpcell)]

        SetPointerType(lpcell, cell)

        c1 = cell()
        c1.name = "foo"
        c2 = cell()
        c2.name = "bar"

        c1.next = pointer(c2)
        c2.next = pointer(c1)

        p = c1

        result = []
        for i in range(8):
            result.append(p.name)
            p = p.next[0]
        self.failUnlessEqual(result, ["foo", "bar"] * 4)

################################################################

def get_suite():
    return unittest.makeSuite(MyTestCase)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    test()
