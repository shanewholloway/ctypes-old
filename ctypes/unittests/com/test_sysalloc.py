import unittest
from ctypes import *
from ctypes.com import mallocspy, ole32

from ctypes.com.automation import BSTR, VARIANT

# We init COM before each test, and uninit afterwards.
# So we must start UN-initialized!
ole32.CoUninitialize()

def find_test_dll():
    import sys, os
    if os.name == "nt":
        name = "_ctypes_test.pyd"
    else:
        name = "_ctypes_test.so"
    for p in sys.path:
        f = os.path.join(p, name)
        if os.path.isfile(f):
            return f

class MallocSpyTest(unittest.TestCase):
    def setUp(self):
        self.expect = None
        self.mallocspy = mallocspy.MallocSpy()
        self.mallocspy.register()
        ole32.CoInitialize(None)

    def tearDown(self):
        try:
            # Even if tests fail or crash, we have to make sure we can
            # shutdown safely.  The problem is that mallocspy cannot be
            # revoked completely while there are still unfreed memory
            # blocks which have been allocated while it was registered.
            #
            # So, we must delete *all* COM objects we still have anywhere,
            # even if an error occurred somewhere, and then shutdown COM,
            # BEFORE Python exits.
            try: 1/0
            except: pass

            ole32.CoUninitialize()
            # Now, check the desired test outcome:
            self.failUnlessEqual(len(self.mallocspy.active_blocks()), self.expect)
        finally:
            self.mallocspy.revoke(warn=0)

    ################

    def test_leak(self):
        # Allocate 10 BSTR's without freeing them, and make sure the
        # leak is detected
        for i in range(10):
            windll.oleaut32.SysAllocString(unicode("Python is cool %s" % i))
        self.expect = 10

    def test_no_leak(self):
        # Allocate 10 BSTR's then free them, and make sure *no* leak
        # is detected
        L = []
        for i in range(10):
            b = windll.oleaut32.SysAllocString(unicode("Python is cool %s" % i))
            L.append(b)
        for b in L:
            windll.oleaut32.SysFreeString(b)
        self.expect = 0

    def test_GetString_C(self):
        # GetString is this function, implemented in C:
        #
        # EXPORT(void) GetString(BSTR *pbstr)
        # {
        #         *pbstr = SysAllocString(L"Goodbye!");
        # }
        GetString = CDLL(find_test_dll()).GetString

        # XXX Explain why we cannot create b outside the loop!
        # And why we cannot do anything against this :-)
        for i in range(32):
            b = BSTR()
            GetString(byref(b))

        self.expect = 0

    def test_GetString_Python(self):
        # Same test as before, but with ctypes implemented C function
        PROTO = WINFUNCTYPE(None, POINTER(BSTR), c_int)

        def func(pbstr, i):
            pbstr[0] = "%s %s" % ("Spam, spam, and spam", i)

        func = PROTO(func)

        for i in range(32):
            b = BSTR()
            func(byref(b), i)
            self.failUnlessEqual(b.value, "%s %s" % ("Spam, spam, and spam", i))

        self.expect = 0

    def test_BSTR_alloc(self):
        for i in range(32):
            BSTR(u"Hello World %d" % i)
        self.expect = 0

    def test_BSTR_pointer(self):
        for i in range(32):
            p = pointer(BSTR())
            p.value = u"Hello World %d" % i
        self.expect = 0

    def test_VARIANT(self):
        # We still have to clear variants manually, to avoid memory leaks.
        for i in range(32):
            v = VARIANT("Hello, World")
            v.value = None
        self.expect = 0

    def test_VARIANT_memleak(self):
        # This demonstrates the memory leak:
        for i in range(32):
            VARIANT("Hello, World")
        self.expect = 32

# Offtopic for this test:
# XXX These need better error messages:
##        POINTER(BSTR()) # TypeError: unhashable type
##        pointer(BSTR)   # TypeError: _type_ must have storage info

################################################################

if __name__ == "__main__":
    unittest.main()
