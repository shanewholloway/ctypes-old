# A tool to parse typelibraries, decompile them and write working
# Python source code wrapping the classes, types, and interfaces with
# ctypes.
#
# The most important restriction of this code is that a COM method is
# *always* assumed to return a HRESULT.  This is checked in the C code,
# but also the whole framework so far has no way to specify a different
# restype, and pass it to the C code.
#
# Fortunately, small integer or long values (smaller than 0x80000000)
# are HRESULTS signalling success instead of errors, but sooner or later
# there will be some problems.

#
# Minor things to do: move the VT_... constants into ctcom.typeinfo
# make it into a real tool with command line arguments
#
#
# See also: http://archive.devx.com/upload/free/features/vcdj/2000/03mar00/fg0300/fg0300.asp
#

from ctypes.com.typeinfo import LoadTypeLib, ITypeInfo, BSTR, \
     LPTYPEATTR, LPFUNCDESC, LPVARDESC, HREFTYPE, VARIANT
from ctypes.com.typeinfo import TKIND_ENUM, TKIND_INTERFACE, TKIND_DISPATCH, TKIND_COCLASS, \
     TKIND_RECORD
from ctypes.com.typeinfo import DISPATCH_METHOD, DISPATCH_PROPERTYGET, \
     DISPATCH_PROPERTYPUT, DISPATCH_PROPERTYPUTREF
from ctypes.com.typeinfo import VAR_PERINSTANCE, VAR_STATIC, VAR_CONST, VAR_DISPATCH
from ctypes.com.typeinfo import IMPLTYPEFLAGS, IMPLTYPEFLAG_FDEFAULT, \
     IMPLTYPEFLAG_FSOURCE, IMPLTYPEFLAG_FRESTRICTED, \
     IMPLTYPEFLAG_FDEFAULTVTABLE

from ctypes.com import GUID

from ctypes import byref, c_int, c_ulong, pointer

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
    VT_DISPATCH: "POINTER(IDispatch)",

    VT_BOOL: "c_int", # VT_BOOL
    VT_VARIANT: "VARIANT",
    VT_UNKNOWN: "POINTER(IUnknown)",

    VT_I1: "c_byte",
    VT_UI1: "c_ubyte",
    VT_UI2: "c_ushort",
    VT_UI4: "c_ulong",
    VT_I8: "c_longlong",
    VT_UI8: "c_ulonglong",
    VT_INT: "c_int",
    VT_UINT: "c_uint",
    VT_VOID: "void",
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

    def _get_type(self, tdesc):
        if tdesc.vt == VT_PTR:
            td = tdesc.u.lptdesc[0]
            if td.vt == VT_USERDEFINED:
                # Pointer to a user defined data type.
                hr = td.u.hreftype
                ti = pointer(ITypeInfo())
                self.ti.GetRefTypeInfo(hr, byref(ti))

                pta = LPTYPEATTR()
                ti.GetTypeAttr(byref(pta))
                ta = pta.contents

                name = BSTR()
                ti.GetDocumentation(-1, byref(name), None, None, None)
                return "POINTER(%s)" % name.value

            return "POINTER(%s)" % self._get_type(td)

        if tdesc.vt == VT_USERDEFINED:
            # use hreftype
            hr = tdesc.u.hreftype
            ti = pointer(ITypeInfo())
            self.ti.GetRefTypeInfo(hr, byref(ti))
            name = BSTR()
            ti.GetDocumentation(-1, byref(name), None, None, None)
            return name.value

        return TYPES[tdesc.vt]

class EnumReader(TypeInfoReader):
    def declaration(self):
        l = []
        l.append("class %s(enum):" % self.name)
        l.append('    """%s"""' % self.docstring)
        l.append("    _iid_ = GUID('%s')" % self.guid)
        for name, value in self.items:
            l.append('    %s = %s' % (name, value))
        l.append("")
        return "\n".join(l)

    def _parse_typeattr(self, ta):
        self.items = []
        for i in range(ta.cVars):
            pvd = LPVARDESC()
            self.ti.GetVarDesc(i, byref(pvd))
            vd = pvd.contents
            name = BSTR()
            self.ti.GetDocumentation(vd.memid, byref(name),
                                     None, None, None)
            name = name.value

            assert vd.varkind == VAR_CONST
            assert vd.elemdescVar.tdesc.vt == VT_INT

            vsrc = vd.u.lpvarValue.contents # the source variant containing the value
            v = VARIANT() # destination variant

            # change the type to VT_INT which is c_int
            from ctypes import oledll
            oleaut32 = oledll.oleaut32
            oleaut32.VariantChangeType(byref(v),
                                       byref(vsrc),
                                       0, VT_INT)

            self.items.append((name, v._.iVal))
            self.ti.ReleaseVarDesc(pvd)

class RecordReader(TypeInfoReader):
    def declaration(self):
        l = []
        l.append("class %s(Structure):" % self.name)
        if self.docstring:
            l.append('    """%s"""' % self.docstring)
        if self.guid != '{00000000-0000-0000-0000-000000000000}':
            l.append("    _iid_ = GUID('%s')" % self.guid)
        l.append("    _fields_ = [")
        for name, value, oInst in self.fields:
            l.append('        (%r, %s),' % (str(name), value))
        l.append("      ]")
        l.append("assert(sizeof(%s) == %d" % (self.name, self.size))
        for name, value, oInst in self.fields:
            l.append("assert(%s.%s.offset == %d)" % (self.name, name, oInst))
        l.append("")
        return "\n".join(l)

    def _parse_typeattr(self, ta):
        self.size = ta.cbSizeInstance
        self.fields = []
        for i in range(ta.cVars):
            pvd = LPVARDESC()
            self.ti.GetVarDesc(i, byref(pvd))
            vd = pvd.contents
            name = BSTR()
            self.ti.GetDocumentation(vd.memid, byref(name),
                                     None, None, None)
            name = name.value

            assert vd.varkind == VAR_PERINSTANCE
            # vd.u.oInst gives the offset into the record.
            # We should use this to separate a structure from a union,
            # and we should check that the offsets are ok.
            # ta.cbSizeInstance should also be checked.
            info = (name, self._get_type(vd.elemdescVar.tdesc), vd.u.oInst)
            self.fields.append(info)
            self.ti.ReleaseVarDesc(pvd)

class Method:
    def __init__(self, name, restype, argtypes):
        self.name = name
        self.restype = restype
        self.argtypes = argtypes

    def declaration(self):
        argtypes = ", ".join(self.argtypes)
        return 'STDMETHOD(%s, "%s", %s)' % (self.restype, self.name, argtypes)

class DispMethod(Method):
    # restype is always HRESULT
    def declaration(self):
        argtypes = ", ".join(self.argtypes)
        return 'STDMETHOD(HRESULT, "%s", %s)' % (self.name, argtypes)

class InterfaceReader(TypeInfoReader):
    baseinterface = "IUnknown"
    nummethods = 3
    method_class = Method

    def _parse_typeattr(self, ta):
        assert ta.cImplTypes == 1
        for i in range(ta.cImplTypes):
            hr = HREFTYPE()
            self.ti.GetRefTypeOfImplType(i, byref(hr))

            ti = pointer(ITypeInfo())
            self.ti.GetRefTypeInfo(hr, byref(ti))

            name = BSTR()
            ti.GetDocumentation(-1, byref(name), None, None, None)
##            self.baseinterface = name.value
            # XXX Sometimes this fails, because baseinterface is IDispatch
            # in an InterfaceReader 
            assert name.value == self.baseinterface, (self, self.baseinterface, name.value)

    def declaration(self):
        l = []
        l.append("class %s(%s):" % (self.name, self.baseinterface))
        l.append('    """%s"""' % self.docstring)
        l.append("    _iid_ = GUID('%s')" % self.guid)
        l.append("")
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
            if fd.oVft/4 < self.nummethods:
                # method belongs to base class
                continue
            
            name = BSTR()
            self.ti.GetDocumentation(fd.memid, byref(name), None, None, None)
            if fd.invkind == DISPATCH_PROPERTYGET:
                name = "_get_" + name.value
            elif fd.invkind == DISPATCH_PROPERTYPUT:
                name = "_put_" + name.value
            elif fd.invkind == DISPATCH_METHOD:
                name = name.value
            elif fd.invkind == DISPATCH_PROPERTYPUTREF:
                name = "_putREF_" + name.value
            else:
                assert 0
            argtypes = self._get_argtypes(fd.cParams, fd.lprgelemdescParam)

            restype = self._get_type(fd.elemdescFunc.tdesc)

##  Combinations:
##
## DispatchInterfaceReader, vt = VT_VOID, invkind = DISPATCH_METHOD
## InterfaceReader, vt = VT_HRESULT, invkind = DISPATCH_METHOD, DISPATCH_PROPERTYGET, DISPATCH_PROPERTYPUT
##            vt = fd.elemdescFunc.tdesc.vt
##            sys.stderr.write("restype for %s -> %s, kind %d\n" % (self, vt, fd.invkind))
            mth = self.method_class(name, restype, argtypes)
            methods.append(mth)
            
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
            result.append(self._get_type(e.tdesc))
        return result

class DispatchInterfaceReader(InterfaceReader):
    baseinterface = "IDispatch"
    nummethods = 7
    method_class = DispMethod

class CoClassReader(TypeInfoReader):
    def _parse_typeattr(self, ta):
        self.interfaces = []
        self.outgoing_interfaces = []
        
        for i in range(ta.cImplTypes):
            hr = HREFTYPE()
            self.ti.GetRefTypeOfImplType(i, byref(hr))

            ti = pointer(ITypeInfo())
            self.ti.GetRefTypeInfo(hr, byref(ti))

            name = BSTR()
            ti.GetDocumentation(-1, byref(name), None, None, None)

            flags = IMPLTYPEFLAGS()
            self.ti.GetImplTypeFlags(i, byref(flags))
            flags = flags.value

            if flags & IMPLTYPEFLAG_FSOURCE:
                which = self.outgoing_interfaces
            else:
                which = self.interfaces

            if flags & IMPLTYPEFLAG_FDEFAULT:
                which.insert(0, name.value)
            else:
                which.append(name.value)

            # XXX There's also the IMPLTYPEFLAG_FDEFAULTVTABLE
            # described in MSDN defaultvtable ODL attribute reference

    def declaration(self):
        l = []
        l.append("class %s(COMObject):" % self.name)
        l.append('    """%s"""' % self.docstring)
        l.append("    _regclsid_ = %r" % self.guid)

        interfaces = ", ".join(self.interfaces)
        l.append("    _com_interfaces_ = [%s]" % interfaces)

        if self.outgoing_interfaces:
            outgoing = ", ".join(self.outgoing_interfaces)
            l.append("    _outgoing_interfaces_ = [%s]" % outgoing)
        l.append("")
        return "\n".join(l)

HEADER = r"""
from ctypes.com import IUnknown, GUID, STDMETHOD, HRESULT
from ctypes.com.typeinfo import IDispatch, BSTR

from ctypes import POINTER, c_voidp, c_byte, c_ubyte, \
     c_short, c_ushort, c_int, c_uint, c_long, c_ulong, \
     c_float, c_double

class COMObject:
    # later this class will be used to create COM objects.
    pass

class enum(c_int):
    pass
"""

class TypeLibReader:
    def __init__(self, filename):
        self.filename = filename
        tlb = self.tlb = LoadTypeLib(filename)

        self.coclasses = {}
        self.interfaces = {}
        self.enums = {}
        self.records = {}

        self.types = {}

        for i in range(tlb.GetTypeInfoCount()):
            kind = c_int()
            tlb.GetTypeInfoType(i, byref(kind))
            ti = pointer(ITypeInfo())
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
            elif kind.value == TKIND_RECORD:
                rdr = RecordReader(self, ti)
                self.records[rdr.guid] = rdr
                
        for iid in self.types:
            ti = self.types[iid]
            rdr = InterfaceReader(self, ti)
            self.types[iid] = rdr

    def dump(self, ofi=None):

        print >> ofi, "# Generated from %s" % self.filename
        print >> ofi, HEADER
        
        if self.enums:
            print >> ofi
            print >> ofi, "#" * 78
            for guid, itf in self.enums.iteritems():
                print >> ofi
                print >> ofi, itf.declaration()

        if self.records:
            print >> ofi
            print >> ofi, "#" * 78
            for guid, itf in self.records.iteritems():
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
        path = r"c:\tss5\bin\debug\Measurement.dll"
##        path = r"c:\sms3a.tlb"
##        path = r"c:\tss5\bin\debug\ITMeasurementControl.dll"
##        path = r"c:\tss5\bin\debug\ITMeasurementSource.dll"

        # None of these will work yet..., only very simple type libs
##        path = r"c:\Programme\Microsoft Office\Office\MSO97.DLL"

        # Microsoft PictureClip Control 6.0 (Ver 1.1)
##        path = r"c:\Windows\System32\PICCLP32.OCX"

    import time
    start = time.clock()
    reader = TypeLibReader(unicode(path))
    stop = time.clock()
    print "# -*- python -*-"
    print "# created from '%s' by '%s'" % (path, sys.argv[0])
    print "# It took %s seconds" % (stop -start)
    reader.dump()
