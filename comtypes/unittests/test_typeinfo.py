import unittest
from ctypes import POINTER, byref
from comtypes import GUID
from comtypes.automation import DISPATCH_METHOD
from comtypes.typeinfo import LoadTypeLibEx, LoadRegTypeLib, \
     QueryPathOfRegTypeLib, TKIND_INTERFACE, TKIND_DISPATCH, TKIND_ENUM

class Test(unittest.TestCase):
    def test_LoadTypeLibEx(self):
        self.assertRaises(WindowsError, lambda: LoadTypeLibEx("<xxx.xx>"))
        tlib = LoadTypeLibEx("shdocvw.dll")
        self.failUnless(tlib.GetTypeInfoCount())
        tlib.GetDocumentation(-1)
        self.failUnlessEqual(tlib.IsName("IWebBrowser"), True)
        self.failUnlessEqual(tlib.IsName("Spam"), False)
        self.failUnless(tlib.FindName("IWebBrowser"))
        self.failUnlessEqual(tlib.FindName("Spam"), None)
        tlib.GetTypeComp()
        
        attr = tlib.GetLibAttr()
        info = attr.guid, attr.wMajorVerNum, attr.wMinorVerNum
        other_tlib = LoadRegTypeLib(*info)
        self.failUnlessEqual(tlib, other_tlib)

##        for n in dir(attr):
##            if not n.startswith("_"):
##                print "\t", n, getattr(attr, n)

        for i in range(tlib.GetTypeInfoCount()):
            ti = tlib.GetTypeInfo(i)
            ti.GetTypeAttr()
            tlib.GetDocumentation(i)
            tlib.GetTypeInfoType(i)

            index, c_tlib = ti.GetContainingTypeLib()
            self.failUnlessEqual(c_tlib, tlib)
            self.failUnlessEqual(index, i)

        self.assertRaises(WindowsError, lambda: tlib.GetTypeInfoOfGuid(GUID()))
        self.failUnless(tlib.GetTypeInfoOfGuid(GUID("{EAB22AC1-30C1-11CF-A7EB-0000C05BAE0B}")))

        path = QueryPathOfRegTypeLib(*info)
        path = path.split("\0")[0]
        self.failUnless(path.lower().endswith("shdocvw.dll"))

    def test_TypeInfo(self):
        tlib = LoadTypeLibEx("shdocvw.dll")
        for index in range(tlib.GetTypeInfoCount()):
            ti = tlib.GetTypeInfo(index)
            ta = ti.GetTypeAttr()
            ti.GetDocumentation(-1)
            if ta.typekind in (TKIND_INTERFACE, TKIND_DISPATCH):
                if ta.cImplTypes:
                    href = ti.GetRefTypeOfImplType(0)
                    base = ti.GetRefTypeInfo(href)
                    base.GetDocumentation(-1)
                    ti.GetImplTypeFlags(0)
            for f in range(ta.cFuncs):
                fd = ti.GetFuncDesc(f)
                names = ti.GetNames(fd.memid, 32)
                ti.GetIDsOfNames(*names)
                ti.GetMops(fd.memid)
            
            for v in range(ta.cVars):
                ti.GetVarDesc(v)

if __name__ == "__main__":
    unittest.main()