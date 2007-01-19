import unittest, gc
from ctypes import *
from ctypes.wintypes import *
from comtypes.client import CreateObject
from comtypes.server.register import register, unregister
from comtypes.test import is_resource_enabled

################################################################

class PROCESS_MEMORY_COUNTERS(Structure):
    _fields_ = [("cb", DWORD),
                ("PageFaultCount", DWORD),
                ("PeakWorkingSetSize", c_size_t),
                ("WorkingSetSize", c_size_t),
                ("QuotaPeakPagedPoolUsage", c_size_t),
                ("QuotaPagedPoolUsage", c_size_t),
                ("QuotaPeakNonPagedPoolUsage", c_size_t),
                ("QuotaNonPagedPoolUsage", c_size_t),
                ("PagefileUsage", c_size_t),
                ("PeakPagefileUsage", c_size_t)]
    def __init__(self):
        self.cb = sizeof(self)

    def dump(self):
        for n, _ in self._fields_[2:]:
            print n, getattr(self, n)/1e6

def wss():
    # Return the working set size (memory used by process)
    pmi = PROCESS_MEMORY_COUNTERS()
    if not windll.psapi.GetProcessMemoryInfo(-1, byref(pmi), sizeof(pmi)):
        raise WinError()
    return pmi.WorkingSetSize

try:
    any
except NameError:
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False

def find_memleak(func):
    # call 'func' several times, so that memory consumption
    # stabilizes:
    for j in xrange(LOOPS[0]):
        for k in xrange(LOOPS[1]):
            func()
    gc.collect(); gc.collect(); gc.collect()
##    leaks = [0] * LOOPS[0]
    bytes = wss()
    # call 'func' several times, recording the difference in
    # memory consumption before and after the call.  Repeat this a
    # few times, and return a list containing the memory
    # consumption differences.
    for j in xrange(LOOPS[0]):
        for k in xrange(LOOPS[1]):
            func()
        gc.collect(); gc.collect(); gc.collect()
##        mem = wss()
##        leaks.append(mem - bytes)
##        bytes = mem
##    return leaks
    return [wss() - bytes]

################################################################
import comtypes.test.TestServer

LOOPS = 10, 1000

class TestInproc(unittest.TestCase):

    def __init__(self, *args, **kw):
        register(comtypes.test.TestServer.TestComServer)
        super(TestInproc, self).__init__(*args, **kw)

    def create_object(self):
        return CreateObject("TestComServerLib.TestComServer")

    def _find_memleak(self, func):
        leaks = find_memleak(func)
        self.failIf(any(leaks), "Leaks %d bytes: %s" % (sum(leaks), leaks))

    if is_resource_enabled("memleaks"):
        def test_get_id(self):
            obj = self.create_object()
            self._find_memleak(lambda: obj.id)

        def test_get_name(self):
            obj = self.create_object()
            self._find_memleak(lambda: obj.name)

        # This leaks memory, but only with comtypes client code,
        # not win32com client code
        def test_set_name(self):
            obj = self.create_object()
            def func():
                obj.name = u"abcde"
            self._find_memleak(func)

        def test_SetName(self):
            obj = self.create_object()
            def func():
                obj.SetName(u"abcde")
            self._find_memleak(func)


        def test_eval(self):
            obj = self.create_object()
            def func():
                obj.eval("(1, 2, 3)")
            self._find_memleak(func)

        def test_get_typeinfo(self):
            obj = self.create_object()
            def func():
                obj.GetTypeInfo(0)
                obj.GetTypeInfoCount()
                obj.QueryInterface(comtypes.IUnknown)
            self._find_memleak(func)

class TestLocalServer(TestInproc):
    def create_object(self):
        return CreateObject("TestComServerLib.TestComServer",
                            clsctx = comtypes.CLSCTX_LOCAL_SERVER)

try:
    from win32com.client import Dispatch
except ImportError:
    pass
else:
    class TestInproc_win32com(TestInproc):
        def create_object(self):
            return Dispatch("TestComServerLib.TestComServer")

        def test_get_typeinfo(self):
            pass

    class TestLocalServer_win32com(TestInproc):
        def create_object(self):
            return Dispatch("TestComServerLib.TestComServer", clsctx = comtypes.CLSCTX_LOCAL_SERVER)

        def test_get_typeinfo(self):
            pass

if __name__ == "__main__":
    unittest.main()
