# Demonstrate some functions from the standard C library.

from ctypes import cdll, POINTER, CFUNCTYPE

import os, sys
from ctypes import c_char_p, c_double, c_char, sizeof

def c_string(init, size=None):
    """c_string(aString) -> character array
    c_string(anInteger) -> character array
    c_string(aString, anInteger) -> character array
    """
    if isinstance(init, str):
        if size is None:
            size = len(init)+1
        buftype = c_char * size
        buf = buftype()
        buf.value = init
        return buf
    elif isinstance(init, int):
        buftype = c_char * init
        buf = buftype()
        return buf
    raise TypeError, init

if os.name == "nt":
    libc = cdll.msvcrt
    printf = libc.printf
    sscanf = libc.sscanf
    snprintf = libc._snprintf
    libmath = cdll.msvcrt

    msvcrt = cdll.msvcrt
    
elif os.name == "posix":
    if sys.platform == "darwin":
        libc = cdll.LoadLibrary("/usr/lib/libc.dylib")
        libmath = cdll.LoadLibrary("/usr/lib/libm.dylib")
    else:
        libc = cdll.LoadLibrary("/lib/libc.so.6")
        libmath = cdll.LoadLibrary("/lib/libm.so.6")
    printf = libc.printf
    sscanf = libc.sscanf
    snprintf = libc.snprintf

from ctypes import Structure, c_int, c_float, byref

def test_printf():
    result = printf("%s%s %d 0x%x %f %d\n",
                    "Hello, ",
##                    u"World!",
                    "World!",
                    c_int(100),
                    c_int(100),
                    c_double(3.14159265),
                    100)

    print "printf returned %d\n" % result

def test_time():
    t = c_int()
    result = libc.time(byref(t))

    print "time since epoch in seconds:", result, t.value

def test_sscanf():
    t1 = c_int(3)
    t2 = c_float(32)
    f = c_double()
    result = sscanf("1234 Hello, 5678 World 3.14159265",
                    "%d Hello, %f World %lf %lf",
                    byref(t1),
                    byref(t2),
                    byref(f))
    print "sscanf found %d fields:" % result,
    print t1.value, t2.value, f.value

def test_snprintf():
    buf = c_string("\000"*32)
    print snprintf(buf, sizeof(buf), "Hello, world")
    print "value: %r" % buf.value

def test_strtok():
    strtok = libc.strtok
    strtok.restype = c_char_p

    delim = " "

    t = c_string("Hi, how are you?")
    s = t # we must hold a ref to the original string
    while 1:
        r = strtok(s, delim)
        if not r:
            break
        s = 0
        print "\t", r
    print
    
def test_sqrt():
    sqrt = libmath.sqrt
    sqrt.restype = c_double
    print sqrt(c_double(2))

# Other examples:
#
# sqrt: returns double
# div: returns a structure containig two ints
# ldiv: returns a structure containing two longs
# _findfirst, 
# _findfirst64, returns __int64
# fopen - returns FILE *
# localtime, gmtime, ... - return struct tm *

def test_qsort():
    import array, random

##    class CMPFUNC(CFuncPtr):
##        _argtypes_ = c_int, c_int
##        _flags_ = FUNCFLAG_CDECL

    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int)

    def compare(a, b):
        ad = c_int.from_address(a)
        bd = c_int.from_address(b)
        return cmp(ad.value, bd.value)


    data = array.array("i", range(5))
    random.shuffle(data)

    print "BEFORE qsort", data
    libc.qsort(data.buffer_info()[0],
               len(data),
               4,
               CMPFUNC(compare))
    print "AFTER qsort", data
    print

def test_qsort_1():
    from _ctypes import Array
    import random

    class IntArray10(Array):
        _type_ = c_int
        _length_ = 10

    l = range(10)
    random.shuffle(l)

    ia10 = IntArray10(*l)

    print "BEFORE sorting:",
    for item in ia10:
        print item,
    print

    # It would be even nicer to define the callback so that
    # it auto-converts the pointer into the value,
    # then we could use callback(cmp, ...)

    def compare(a, b):
        ad = c_int.from_address(a)
        bd = c_int.from_address(b)
        return cmp(ad.value, bd.value)
    
##    class CMPFUNC(CFuncPtr):
##        _argtypes_ = c_int, c_int
##        _flags_ = FUNCFLAG_CDECL

    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int)
    
    libc.qsort(ia10,
               len(ia10),
               4,
               CMPFUNC(compare))
    
    print "AFTER  sorting:", 
    for item in ia10:
        print item,
    print
    print

def test_qsort_2():
    import random

    IntArray10 = c_int * 10

    ia10 = IntArray10()

    for i in range(10):
        num = random.choice(range(100))
        ia10[i] = c_int(num)
    print "BEFORE sorting:",
    for item in ia10:
        print item,
    print

    # It would be even nicer to define the callback so that
    # it auto-converts the pointer into the value,
    # then we could use callback(cmp, ...)

    def compare(a, b):
        ad = c_int.from_address(a)
        bd = c_int.from_address(b)
        return cmp(ad.value, bd.value)
    
##    class CMPFUNC(CFuncPtr):
##        _argtypes_ = c_int, c_int
##        _flags_ = FUNCFLAG_CDECL

    CMPFUNC = CFUNCTYPE(c_int, c_int, c_int)

    libc.qsort(ia10,
               len(ia10),
               4,
               CMPFUNC(compare))

    print "AFTER  sorting:", 
    for item in ia10:
        print item,
    print
    print

def test_qsort_5():
    # demonstrates callback functions specified by using types in the _types_ list
    import random

    IntArray10 = c_int * 10

    ia10 = IntArray10()

    for i in range(10):
        num = random.choice(range(100))
        ia10[i] = num
    print "BEFORE sorting:",
    for item in ia10:
        print item,
    print

    def compare(a, b):
        "the callback now receives pointers to c_int:"
        return cmp(a.contents.value, b.contents.value)
    
##    class CMPFUNC(CFuncPtr):
##        _argtypes_ = POINTER(c_int), POINTER(c_int)
##        _flags_ = FUNCFLAG_CDECL

    CMPFUNC = CFUNCTYPE(c_int, POINTER(c_int), POINTER(c_int))

    libc.qsort(ia10,
               len(ia10),
               4,
               CMPFUNC(compare))

    print "AFTER  sorting:", 
    for item in ia10:
        print item,
    print
    print


if __name__ == '__main__':
    test_printf()
    test_time()
    test_sscanf()
    test_snprintf()
    test_strtok()
    test_sqrt()
    test_qsort()
    test_qsort_1()
    test_qsort_2()
    test_qsort_5()
