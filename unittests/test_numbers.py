from ctypes import *
import unittest
import sys, struct

def valid_ranges(*types):
    # given a sequence of numeric types, collect their _type_
    # attribute, which is a single format character compatible with
    # the struct module, use the struct module to calculate the
    # minimum and maximum value allowed for this format.
    # Returns a list of (min, max) values.
    result = []
    for t in types:
        fmt = t._type_
        size = struct.calcsize(fmt)
        a = struct.unpack(fmt, ("\x00"*32)[:size])[0]
        b = struct.unpack(fmt, ("\xFF"*32)[:size])[0]
        c = struct.unpack(fmt, ("\x7F"+"\x00"*32)[:size])[0]
        d = struct.unpack(fmt, ("\x80"+"\xFF"*32)[:size])[0]
        result.append((min(a, b, c, d), max(a, b, c, d)))
    return result

ArgType = type(c_int(0)._as_parameter_)

unsigned_types = [c_ubyte, c_ushort, c_uint, c_ulong]
signed_types = [c_byte, c_short, c_int, c_long, c_longlong]

float_types = [c_double, c_float]

try:
    c_ulonglong
    c_longlong
except NameError:
    pass
else:
    unsigned_types.append(c_ulonglong)
    signed_types.append(c_longlong)
    
unsigned_ranges = valid_ranges(*unsigned_types)
signed_ranges = valid_ranges(*signed_types)

try:
    string_types = [c_string, c_wstring]
except NameError:
    string_types = [c_string]

################################################################

class NumberTestCase(unittest.TestCase):
    
    def test_default_init(self):
        # default values are set to zero
        for t in signed_types + unsigned_types + float_types:
            self.failUnless(t().value == 0)

    def test_unsigned_values(self):
        # the value given to the constructor is available
        # as the 'value' attribute
        for t, (l, h) in zip(unsigned_types, unsigned_ranges):
            self.failUnless(t(l).value == l)
            self.failUnless(t(h).value == h)

    def test_signed_values(self):
        # see above
        for t, (l, h) in zip(signed_types, signed_ranges):
            self.failUnless(t(l).value == l)
            self.failUnless(t(h).value == h)

    def test_typeerror(self):
        # Only numbers are allowed in the contructor,
        # otherwise TypeError is raised
        for t in signed_types + unsigned_types + float_types:
            self.assertRaises(TypeError, t, "")
            self.assertRaises(TypeError, t, None)

    def test_valid_ranges(self):
        # invalid values of the correct type
        # raise ValueError (not OverflowError)
        for t, (l, h) in zip(unsigned_types, unsigned_ranges):
            self.assertRaises(ValueError, t, l-1)
            self.assertRaises(ValueError, t, h+1)

    def test_from_param(self):
        # the from_param class method attribute always
        # returns PyCArgObject instances
        for t in signed_types + unsigned_types + float_types:
            self.failUnless(ArgType == type(t.from_param(0)))

    def test_as_parameter(self):
        # The _as_parameter_ property must also
        # be a PyCArgObject instance
        for t in signed_types + unsigned_types + float_types:
            parm = t()._as_parameter_
            self.failUnless(ArgType == type(parm))

            # _as_parameter_ is readonly!
            self.assertRaises(TypeError, setattr, t(), "_as_parameter_", None)

    def test_byref(self):
        # calling byref returns also a PyCArgObject instance
        for t in signed_types + unsigned_types + float_types:
            parm = byref(t())
            self.failUnless(ArgType == type(parm))


    def test_floats(self):
        # c_float and c_double can be created from
        # Python int, long and float
        for t in float_types:
            self.failUnless(t(2.0).value == 2.0)
            self.failUnless(t(2).value == 2.0)
            self.failUnless(t(2L).value == 2.0)

    def test_integers(self):
        # integers cannot be constructed from floats
        for t in signed_types + unsigned_types:
            self.assertRaises(TypeError, t, 3.14)

            
def get_suite():
    return unittest.makeSuite(NumberTestCase, 'test')

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
