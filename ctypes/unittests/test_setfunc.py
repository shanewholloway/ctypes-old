# Test the (internal) setfunc function.
import unittest
from ctypes import *

s_types = (c_byte, c_short, c_int, c_long, c_longlong)
u_types = (c_ubyte, c_ushort, c_uint, c_ulong, c_ulonglong)

# ctypes int classes __init__ and from_param should accept exactly the same objects.
class TestIntegers(unittest.TestCase):
    
    def test_init(self):
        # we can now initialize any ctypes int type...
        for cls in s_types + u_types:

            # ...from any ctypes int type, or python int.
            for obj in [typ(42) for typ in s_types + u_types] + [42, 42L]:
                self.failUnlessEqual(cls(obj).value, 42)

            # but not from other types
            for obj in (c_char("x"), c_char_p("x"), "x", c_float(42), c_double(42), 42.0):
                self.assertRaises(TypeError, lambda: cls(obj))

    def test_fromparam(self):
        for cls in s_types + u_types:
            for obj in [typ(42) for typ in s_types + u_types] + [42, 42L]:
                # from_param currently either returns the object itself,
                # or a PyCArgObject.
                param = cls.from_param(obj)
                if obj == param:
                    continue
                self.failUnlessEqual(repr(param), "<cparam '%s' (42)>" % cls._type_)

            for obj in (c_char("x"), c_char_p("x"), "x", c_float(42), c_double(42), 42.0):
                self.assertRaises(TypeError, lambda: cls.from_para,(obj))

    def test_setfield(self):
        for cls in s_types + u_types:
            class X(Structure):
                _fields_ = [("v", cls)]
            x = X()
            for obj in [typ(42) for typ in s_types + u_types] + [42, 42L]:
                x.v = obj
                self.failUnlessEqual(x.v, 42)

            for obj in (c_char("x"), c_char_p("x"), "x", c_float(42), c_double(42), 42.0):
                self.assertRaises(TypeError, setattr, x, "v", obj)

if __name__ == "__main__":
    unittest.main()
