import unittest
from ctypes import *
from struct import calcsize
from _ctypes import alignment

class StructureTestCase(unittest.TestCase):
    formats = {"c": c_char,
               "b": c_byte,
               "B": c_ubyte,
               "h": c_short,
               "H": c_ushort,
               "i": c_int,
               "I": c_uint,
               "l": c_long,
               "L": c_ulong,
               "q": c_longlong,
               "Q": c_ulonglong,
               "f": c_float,
               "d": c_double,
               }
    
    def test_simple_structs(self):
        for code, tp in self.formats.items():
            class X(Structure):
                _fields_ = [("x", c_char),
                            ("y", tp)]
            self.failUnless(sizeof(X) == calcsize("c%c0%c" % (code, code)))

    def test_unions(self):
        for code, tp in self.formats.items():
            class X(Union):
                _fields_ = [("x", c_char),
                            ("y", tp)]
            self.failUnless(sizeof(X) == calcsize("%c" % (code)))

    def test_struct_alignment(self):
        class X(Structure):
            _fields_ = [("x", c_char * 3)]
        self.failUnless(alignment(X) == calcsize("s"))
        self.failUnless(sizeof(X) == calcsize("3s"))

        class Y(Structure):
            _fields_ = [("x", c_char * 3),
                        ("y", c_int)]
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

    def test_fields(self):
        # test the offset and size attributes of Structure/Unoin fields.
        class X(Structure):
            _fields_ = [("x", c_int),
                        ("y", c_char)]

        self.failUnless(X.x.offset == 0)
        self.failUnless(X.x.size == sizeof(c_int))

        self.failUnless(X.y.offset == sizeof(c_int))
        self.failUnless(X.y.size == sizeof(c_char))

        # readonly
        self.assertRaises(TypeError, setattr, X.x, "offset", 92)
        self.assertRaises(TypeError, setattr, X.x, "size", 92)

        class X(Union):
            _fields_ = [("x", c_int),
                        ("y", c_char)]

        self.failUnless(X.x.offset == 0)
        self.failUnless(X.x.size == sizeof(c_int))

        self.failUnless(X.y.offset == 0)
        self.failUnless(X.y.size == sizeof(c_char))

        # readonly
        self.assertRaises(TypeError, setattr, X.x, "offset", 92)
        self.assertRaises(TypeError, setattr, X.x, "size", 92)

        # XXX Should we check nested data types also?
        # offset is always relative to the class...

    def test_packed(self):
        class X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 1

        self.failUnless(sizeof(X) == 9, sizeof(X))
        self.failUnless(X.b.offset == 1, X.b.offset)

        class X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 2
        self.failUnless(sizeof(X) == 10, sizeof(X))
        self.failUnless(X.b.offset == 2, X.b.offset)

        class X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 4
        self.failUnless(sizeof(X) == 12)
        self.failUnless(X.b.offset == 4)

        import struct
        longlong_size = struct.calcsize("q")
        longlong_align = struct.calcsize("bq") - longlong_size

        class X(Structure):
            _fields_ = [("a", c_byte),
                        ("b", c_longlong)]
            _pack_ = 8

        self.failUnless(sizeof(X) == longlong_align + longlong_size)
        self.failUnless(X.b.offset == min(8, longlong_align))


        d = {"_fields_": [("a", "b"),
                          ("b", "q")],
             "_pack_": -1}
        self.assertRaises(ValueError, type(Structure), "X", (Structure,), d)

    def test_initializers(self):
        class Person(Structure):
            _fields_ = [("name", c_char*6),
                        ("age", c_int)]

        self.assertRaises(TypeError, Person, 42)
        self.assertRaises(ValueError, Person, "asldkjaslkdjaslkdj")
        self.assertRaises(TypeError, Person, "Name", "HI")

    def test_nested_initializers(self):
        # test initializing nested structures
        class Phone(Structure):
            _fields_ = [("areacode", c_char*6),
                        ("number", c_char*12)]

        class Person(Structure):
            _fields_ = [("name", c_char * 12),
                        ("phone", Phone),
                        ("age", c_int)]

        p = Person("Someone", ("1234", "5678"), 5)

        self.failUnlessEqual(p.name, "Someone")
        self.failUnlessEqual(p.phone.areacode, "1234")
        self.failUnlessEqual(p.phone.number, "5678")
        self.failUnlessEqual(p.age, 5)

    def test_structures_with_wchar(self):
        try:
            c_wchar
        except NameError:
            return # no unicode

        class PersonW(Structure):
            _fields_ = [("name", c_wchar * 12),
                        ("age", c_int)]

        p = PersonW(u"Someone")
        self.failUnlessEqual(p.name, "Someone")
        

    def test_init_errors(self):
        class Phone(Structure):
            _fields_ = [("areacode", c_char*6),
                        ("number", c_char*12)]

        class Person(Structure):
            _fields_ = [("name", c_char * 12),
                        ("phone", Phone),
                        ("age", c_int)]

        cls, msg = self.get_except(Person, "Someone", (1, 2))
        self.failUnlessEqual(cls, TypeError)
        self.failUnlessEqual(msg, "(Phone) expected string or Unicode object, int found")

        cls, msg = self.get_except(Person, "Someone", ("a", "b", "c"))
        self.failUnlessEqual(cls, ValueError)
        self.failUnlessEqual(msg, "(Phone) too many initializers")


    def get_except(self, func, *args):
        try:
            func(*args)
        except Exception, detail:
            return detail.__class__, str(detail)
                

if __name__ == '__main__':
    unittest.main()

