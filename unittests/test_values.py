"""
A testcase which accesses *values* in a dll.
"""

import unittest
from ctypes import *

pydll = cdll.python22

class ValuesTestCase(unittest.TestCase):
    """A doc string"""

    def test_optimizeflag(self):
        """This test accesses the Py_OptimizeFlag intger, which is
        exported by the Python dll.

        It's value is set depending on the -O and -OO flags:
        if not given, it is 0 and __debug__ is 1.
        If -O is given, the flag is 1, for -OO it is 2.
        docstrings are also removed in the latter case."""
        opt = c_int.in_dll(pydll, "Py_OptimizeFlag").value
        if __debug__:
            self.failUnlessEqual(opt, 0)
        elif ValuesTestCase.__doc__ is not None:
            self.failUnlessEqual(opt, 1)
        else:
            self.failUnlessEqual(opt, 2)

    def test_frozentable(self):
        """Python exports a PyImport_FrozenModules symbol. This is a
        pointer to an array of struct _frozen entries.  The end of the
        array is marked by an entry containing a NULL name and zero
        size.

        In standard Python, this table contains a __hello__ module,
        and a __phello__ package containing a spam module."""
        class struct_frozen(Structure):
            _fields_ = [("name", c_char_p),
                        ("code", POINTER(c_ubyte)),
                        ("size", c_int)]

        FrozenTable = POINTER(struct_frozen)

        ft = FrozenTable.in_dll(pydll, "PyImport_FrozenModules")
        # ft is a pointer to the struct_frozen entries:
        items = []
        for entry in ft:
            # This is dangerous. We *can* iterate over a pointer, but
            # the loop will not terminate (maybe with an access
            # violation;-) because the pointer instance has no size.
            if entry.name is None:
                break
            items.append((entry.name, entry.size))
        expected = [("__hello__", 100), ("__phello__", -100), ("__phello__.spam", 100)]
        self.failUnlessEqual(items, expected)

    def test_undefined(self):
        self.assertRaises(ValueError, c_int.in_dll, pydll, "Undefined_Symbol")

##    def test_function_pointer(self):
##        # A C function type of no arguments, which returns an integer
##        HOOKFUNC = CFUNCTYPE(c_int)

##        hook_ptr = HOOKFUNC.in_dll(pydll, "PyOS_InputHook")

##        def my_hook():
##            print "*hook called*"
##            return 0

##        c_hook = HOOKFUNC(my_hook)

##        print hex(addressof(c_hook))

##        hook_ptr.contents = c_hook

##    def test_function_pointer_2(self):
##        HOOKFUNC = CFUNCTYPE(c_int)

##        class X(Structure):
##            _fields_ = [("func", HOOKFUNC)]

##        hook_ptr = X.in_dll(pydll, "PyOS_InputHook")

##        def my_hook():
##            print "*hook called*"
##            return 0

##        c_hook = HOOKFUNC(my_hook)

##        hook_ptr.func = c_hook
##        raw_input()

##    def test_func_ptr_3(self):
##        f = pydll.PyOS_InputHook

##        print dir(f)

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

def get_suite():
    return unittest.makeSuite(ValuesTestCase)

if __name__ == '__main__':
    unittest.main()
