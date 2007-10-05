import unittest
from ctypes import *
from ctypes.wintypes import *
from comtypes.client import CreateObject, GetEvents, ShowEvents
from comtypes.server.register import register#, unregister
from comtypes.test import is_resource_enabled
from comtypes.test.find_memleak import find_memleak

################################################################
import comtypes.test.TestComServer
register(comtypes.test.TestComServer.TestComServer)

class TestInproc(unittest.TestCase):

    def create_object(self):
        return CreateObject("TestComServerLib.TestComServer",
                            clsctx = comtypes.CLSCTX_INPROC_SERVER)

    def _find_memleak(self, func):
        bytes = find_memleak(func)
        self.failIf(bytes, "Leaks %d bytes" % bytes)

    def test_getname(self):
        from ctypes import byref, pointer
        from comtypes import BSTR

        # This tests a tricky bug, introduced with this patch:
        # http://www.python.org/sf/1643874
        #
        # Returning a BSTR as an [out] parameter from a server
        # implementation must transfer the ownership to the caller.
        # When this is not done, the BSTR instance is SysFreeString'd
        # too early, and the memory is reused.
        obj = self.create_object()
        pb = pointer(BSTR())
        # Get the BSTR from the server:
        obj._ITestComServer__com__get_name(pb)
        # Retrieve the value, but keep the pointer to the BSTR alive:
        name = pb[0]
        # Create sme BSTR's to reuse the memory in case it has been freed:
        for i in range(10):
            BSTR("f" * len(name))
        # Make sure the pointer is still valid:
        self.failUnlessEqual(pb[0], name)

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

if is_resource_enabled("ui"):
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

        # These tests make no sense with win32com, override to disable them:
        def test_get_typeinfo(self):
            pass

        def test_getname(self):
            pass

    if is_resource_enabled("ui"):
        class TestLocalServer_win32com(TestInproc_win32com):
            def create_object(self):
                return Dispatch("TestComServerLib.TestComServer", clsctx = comtypes.CLSCTX_LOCAL_SERVER)

import doctest
import comtypes.test.test_comserver


class TestCase(unittest.TestCase):
    def test(self):
        doctest.testmod(comtypes.test.test_comserver, optionflags=doctest.ELLIPSIS)

    # The following functions are never called, they only contain doctests:

    def ShowEvents(self):
        '''
        >>> from comtypes.client import CreateObject, ShowEvents
        >>>
        >>> o = CreateObject("TestComServerLib.TestComServer")
        >>> con = ShowEvents(o)
        # event found: EvalStarted
        # event found: EvalCompleted
        >>> result = o.eval("10 / 4")
        Event EvalStarted(<comtypes.client._events.EventReceiver object at ..., u'10 / 4')
        Event EvalCompleted(<comtypes.client._events.EventReceiver object at ..., u'10 / 4', VARIANT(2))
        >>> result
        2
        >>>
        '''

    def GetEvents():
        """
        >>> from comtypes.client import CreateObject, GetEvents
        >>>
        >>> o =  CreateObject("TestComServerLib.TestComServer")
        >>> class EventHandler(object):
        ...     def EvalStarted(self, this, what):
        ...         print "EvalStarted:", what
        ...         return 0
        ...     def EvalCompleted(self, this, what, result):
        ...         print "EvalCompleted:", what, "=", result.value
        ...         return 0
        ...
        >>>
        >>> con = GetEvents(o, EventHandler())
        >>> o.eval("2 + 3")
        EvalStarted: 2 + 3
        EvalCompleted: 2 + 3 = 5
        5
        >>> del con
        >>> o.eval("3 + 2")
        5
        >>>
        """

if __name__ == "__main__":
    unittest.main()
