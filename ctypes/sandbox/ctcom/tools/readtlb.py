from ctcom.typeinfo import LoadTypeLib, ITypeInfoPointer, BSTR, \
     LPTYPEATTR, LPFUNCDESC, HREFTYPE
from ctcom.typeinfo import TKIND_ENUM, TKIND_INTERFACE, TKIND_DISPATCH, TKIND_COCLASS
from ctcom.typeinfo import DISPATCH_METHOD, DISPATCH_PROPERTYGET, \
     DISPATCH_PROPERTYPUT, DISPATCH_PROPERTYPUTREF

from ctypes import byref, c_int, c_ulong

VT_EMPTY	= 0
VT_NULL	= 1
VT_I2	= 2
VT_I4	= 3
VT_R4	= 4
VT_R8	= 5
VT_CY	= 6
VT_DATE	= 7
VT_BSTR	= 8
VT_DISPATCH	= 9
VT_ERROR	= 10
VT_BOOL	= 11
VT_VARIANT	= 12
VT_UNKNOWN	= 13
VT_DECIMAL	= 14
VT_I1	= 16
VT_UI1	= 17
VT_UI2	= 18
VT_UI4	= 19
VT_I8	= 20
VT_UI8	= 21
VT_INT	= 22
VT_UINT	= 23
VT_VOID	= 24
VT_HRESULT	= 25
VT_PTR	= 26
VT_SAFEARRAY	= 27
VT_CARRAY	= 28
VT_USERDEFINED	= 29
VT_LPSTR	= 30
VT_LPWSTR	= 31
VT_RECORD	= 36
VT_FILETIME	= 64
VT_BLOB	= 65
VT_STREAM	= 66
VT_STORAGE	= 67
VT_STREAMED_OBJECT	= 68
VT_STORED_OBJECT	= 69
VT_BLOB_OBJECT	= 70
VT_CF	= 71
VT_CLSID	= 72

TYPES = {
    VT_I2: "c_short",
    VT_I4: "c_long",
    VT_R4: "c_float",
    VT_R8: "c_double",
    VT_BSTR: "BSTR",
    VT_DISPATCH: "IDispatchPointer",

    VT_BOOL: "c_int", # VT_BOOL
    VT_VARIANT: "VARIANT",
    VT_UNKNOWN: "IUnknownPointer",

    VT_I1: "c_byte",
    VT_UI1: "c_ubyte",
    VT_UI2: "c_ushort",
    VT_UI4: "c_ulong",
    VT_I8: "c_longlong",
    VT_UI8: "c_ulonglong",
    VT_INT: "c_int",
    VT_UINT: "c_uint",
    VT_VOID: "c_voidp",
    VT_HRESULT: "HRESULT", 
    VT_PTR: "VT_PTR",
    VT_LPSTR: "c_char_p",
    VT_LPWSTR: "c_wchar_p",
    }

class TypeInfoReader:
    def __init__(self, library, typeinfo):
        self.library = library
        self.ti = typeinfo

        self._get_typeattr()
        self._get_documentation()

    def _get_typeattr(self):
        pta = LPTYPEATTR()
        self.ti.GetTypeAttr(byref(pta))
        ta = pta.contents
        self.guid = str(ta.guid)
        self._parse_typeattr(ta)
        self.ti.ReleaseTypeAttr(pta)

    def _get_documentation(self):
        name = BSTR()
        docstring = BSTR()
        helpcontext = c_ulong()
        helpfile = BSTR()
        self.ti.GetDocumentation(-1, byref(name),
                                 byref(docstring), byref(helpcontext),
                                 byref(helpfile))
        self.name = name.value
        self.docstring = docstring.value

    def _parse_typeattr(self, ta):
        pass

class EnumReader(TypeInfoReader):
    def declaration(self):
        l = []
        l.append("class %s(enum):" % self.name)
        l.append('    """%s"""' % self.docstring)
        l.append("    _iid_ = GUID('%s')" % self.guid)
        l.append("")
        return "\n".join(l)

class Method:
    def __init__(self, name, restype, argtypes):
        self.name = name
        self.argtypes = argtypes

    def declaration(self):
        argtypes = ", ".join(self.argtypes)
        return '"%s", [%s]' % (self.name, argtypes)

class InterfaceReader(TypeInfoReader):
    
    def _parse_typeattr(self, ta):
        assert ta.cImplTypes == 1
        for i in range(ta.cImplTypes):
            hr = HREFTYPE()
            self.ti.GetRefTypeOfImplType(i, byref(hr))

            ti = ITypeInfoPointer()
            self.ti.GetRefTypeInfo(hr, byref(ti))

            name = BSTR()
            ti.GetDocumentation(-1, byref(name), None, None, None)
            self.baseinterface = name.value

    def declaration(self):
        l = []
        l.append("class %s(%s):" % (self.name, self.baseinterface))
        l.append('    """%s"""' % self.docstring)
        l.append("    _iid_ = GUID('%s')" % self.guid)
        l.append("")
        l.append("class %sPointer(COMPointer):" % self.name)
        l.append("    _interface_ = %s" % self.name)
        return "\n".join(l)
    
    def definition(self):
        pta = LPTYPEATTR()
        self.ti.GetTypeAttr(byref(pta))
        ta = pta.contents

        methods = []

        for i in range(ta.cFuncs):
            pfd = LPFUNCDESC()
            self.ti.GetFuncDesc(i, byref(pfd))
            fd = pfd.contents
            name = BSTR()
            self.ti.GetDocumentation(fd.memid, byref(name), None, None, None)
            if fd.invkind == DISPATCH_PROPERTYGET:
                name = "_get_" + name.value
            elif fd.invkind == DISPATCH_PROPERTYPUT:
                name = "_put_" + name.value
            elif fd.invkind == DISPATCH_METHOD:
                name = name.value
            else:
                assert 0
            argtypes = self._get_argtypes(fd.cParams, fd.lprgelemdescParam)

            restype = fd.elemdescFunc.tdesc.vt
            assert restype in (VT_HRESULT, VT_VOID, VT_UI4, VT_I4), restype
            mth = Method(name, restype, argtypes)
##            oVft/4
            methods.append(mth)
##            print "%s(%d)" % (name.value, fd.cParams)
##            print fd.elemdescFunc.tdesc.vt
##            assert fd.elemdescFunc.tdesc.vt in (24, 25), fd.elemdescFunc.tdesc.vt # HRESULT
            
            self.ti.ReleaseFuncDesc(pfd)

        self.ti.ReleaseTypeAttr(pta)

        l = []
        l.append("%s._methods_ = [" % self.name)
        for m in methods:
            l.append('    (%s),' % m.declaration())
        l.append("]")
        return "\n".join(l)

    def _get_argtypes(self, n, pelemdesc):
        result = []
        for i in range(n):
            e = pelemdesc[i]
            vt = e.tdesc.vt
##            if vt == VT_PTR:
            result.append(self._get_type(e.tdesc))
        return result

    def _get_type(self, tdesc):
        if tdesc.vt == VT_PTR:
            return "POINTER(%s)" % self._get_type(tdesc.u.lptdesc[0])
        if tdesc.vt == VT_USERDEFINED:
            # use hreftype
            hr = tdesc.u.hreftype
            ti = ITypeInfoPointer()
            self.ti.GetRefTypeInfo(hr, byref(ti))

            name = BSTR()
            ti.GetDocumentation(-1, byref(name), None, None, None)

            return name.value

##        return TYPES.get(tdesc.vt, tdesc.vt)
        return TYPES[tdesc.vt]

class DispatchInterfaceReader(InterfaceReader):
    pass

class CoClassReader(TypeInfoReader):
    def _parse_typeattr(self, ta):
        self.interfaces = []
        for i in range(ta.cImplTypes):
            hr = HREFTYPE()
            self.ti.GetRefTypeOfImplType(i, byref(hr))

            ti = ITypeInfoPointer()
            self.ti.GetRefTypeInfo(hr, byref(ti))

            name = BSTR()
            ti.GetDocumentation(-1, byref(name), None, None, None)
            self.interfaces.append(name.value)

    def declaration(self):
        l = []
        l.append("class %s(COMObject):" % self.name)
        l.append('    """%s"""' % self.docstring)
        l.append("    _regclsid_ = %r" % self.guid)

        interfaces = ", ".join(self.interfaces)

        l.append("    _com_interfaces_ = [%s]" % interfaces)
        l.append("")
        return "\n".join(l)

HEADER = r"""
from ctcom import IUnknown, GUID, COMPointer
from ctcom.typeinfo import IDispatch, BSTR

from ctypes import POINTER, c_voidp, c_byte, c_ubyte, \
     c_short, c_ushort, c_int, c_uint, c_long, c_ulong, \
     c_float, c_double

class COMObject:
    pass

class enum:
    pass
"""

class TypeLibReader:
    def __init__(self, filename):
        self.filename = filename
        tlb = self.tlb = LoadTypeLib(filename)

        self.coclasses = {}
        self.interfaces = {}
        self.enums = {}

        self.types = {}

        for i in range(tlb.GetTypeInfoCount()):
            kind = c_int()
            tlb.GetTypeInfoType(i, byref(kind))
            ti = ITypeInfoPointer()
            tlb.GetTypeInfo(i, byref(ti))

            if kind.value == TKIND_COCLASS:
                rdr = CoClassReader(self, ti)
                self.coclasses[rdr.guid] = rdr
            elif kind.value == TKIND_DISPATCH:
                rdr = DispatchInterfaceReader(self, ti)
                self.interfaces[rdr.guid] = rdr
            elif kind.value == TKIND_INTERFACE:
                rdr = InterfaceReader(self, ti)
                self.interfaces[rdr.guid] = rdr
            elif kind.value == TKIND_ENUM:
                rdr = EnumReader(self, ti)
                self.enums[rdr.guid] = rdr
##                print "# ??? Enum"

        for iid in self.types:
            ti = self.types[iid]
            rdr = InterfaceReader(self, ti)
            self.types[iid] = rdr

        return

        if p.contents.typekind == TKIND_INTERFACE:
            rdr = InterfaceReader(hti)
##            print "-"*22, rdr.name
            return rdr.name+'Pointer'
        elif p.contents.typekind == TKIND_ENUM:
            rdr = EnumReader(hti)
##            print "-"*22, rdr.name
            return rdr.name
        else:
            print "TKIND?", p.contents.typekind

    def dump(self, ofi=None):

        print >> ofi, "# Generated from %s" % self.filename
        print >> ofi, HEADER
        
        if self.enums:
            print >> ofi
            print >> ofi, "#" * 78
            for guid, itf in self.enums.iteritems():
                print >> ofi
                print >> ofi, itf.declaration()

        if self.interfaces:
            print >> ofi
            print >> ofi, "#" * 78
            for guid, itf in self.interfaces.iteritems():
                print >> ofi
                print >> ofi, itf.declaration()

            for guid, itf in self.interfaces.iteritems():
                print >> ofi
                print >> ofi, itf.definition()

        if self.coclasses:
            print >> ofi
            print >> ofi, "#" * 78
            for guid, cls in self.coclasses.iteritems():
                print >> ofi
                print >> ofi, cls.declaration()

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = r"c:\tss5\bin\debug\ITInfo.dll"
        path = r"c:\sms3a.tlb"
##        path = r"c:\tss5\bin\debug\ITMeasurementControl.dll"
##        path = r"c:\tss5\bin\debug\ITMeasurementSource.dll"

    import time
    start = time.clock()
    reader = TypeLibReader(unicode(path))
    stop = time.clock()
##    print "It took %s seconds" % (stop -start)
    reader.dump()
## Hm, What about creating the CLASSes itself in TypeLibReader?

    # c:/tss5/components/_Pythonlib/ctcom
