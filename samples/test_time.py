from ctypes import cdll, c_int, Structure, byref, pointer, POINTER

class tm(Structure):
    _fields_ = [("tm_sec", "i"),
                ("tm_min", "i"),
                ("tm_hour", "i"),
                ("tm_mday", "i"),
                ("tm_mon", "i"),
                ("tm_year", "i"),
                ("tm_wday", "i"),
                ("tm_yday", "i"),
                ("tm_isdst", "i")]

    def dump(self, indent=""):
        INDENT = "   "
        print "%s%s:" % (indent, self.__class__.__name__)
        for name, fmt in self._fields_:
            val = getattr(self, name)
            if isinstance(val, Structure):
                val.dump(indent + INDENT)
            elif isinstance(val, long) or isinstance(val, int):
                print "%s%30s: %s (0x%x)" % (indent, name, val, val)
            else:
                print "%s%30s: %r" % (indent, name, val)
        print

import os, sys
if os.name == "nt":
    clib = cdll.msvcrt
elif os.name == "posix":
    if sys.platform == "darwin":
        clib = cdll.LoadLibrary("/usr/lib/libc.dylib")
    else:
        clib = cdll.LoadLibrary("/lib/libc.so.6")

def test_time():
    # Assigning argtypes to a function retrieves the 'from_param' attribute
    # from every type and store it. When the function is called, the attribute
    # is called with each actual parameter, and the result is pushed on the stack.
    # Retrieving the argtypes value again returns a tuple of these from_param attributes,
    # so
    # func.argtypes = (c_int,); y = func.argtypes
    # will set y to (c_int.from_param,).
    
    if clib.localtime.argtypes:
        print "Testing with function prototypes"
        print "================================"
    else:
        print "Testing without function prototypes"
        print "==================================="
    clib.localtime.restype = POINTER(tm)

    ltime = c_int()
    result = clib.time(byref(ltime))
    print ltime.value, result

    import time
    print time.time()

    pnow = clib.localtime(byref(ltime))
    pnow.contents.dump()

    t = clib.asctime(pnow)
    print repr(t)

if __name__ == '__main__':
    test_time()

    # prototype
    clib.asctime.argtypes = [POINTER(tm)]
    clib.asctime.restype = "z"

    # prototype
    clib.time.argtypes = [POINTER(c_int)]
    clib.time.restype = "i"

    # prototype
    clib.localtime.argtypes = [POINTER(c_int)]

    test_time()
