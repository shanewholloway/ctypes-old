# A tool to parse typelibraries, decompile them and write working
# Python source code wrapping the classes, types, and interfaces with
# ctypes.
#

#
# Minor things to do: move the VT_... constants into ctcom.typeinfo
# make it into a real tool with command line arguments
#
#
# See also: http://archive.devx.com/upload/free/features/vcdj/2000/03mar00/fg0300/fg0300.asp
#

from ctypes.com.automation import LoadTypeLibEx, LoadTypeLib, ITypeInfo, BSTR, \
     LPTYPEATTR, LPFUNCDESC, LPVARDESC, HREFTYPE, VARIANT, LPTLIBATTR

from ctypes.com.automation import TKIND_ENUM, TKIND_INTERFACE, TKIND_DISPATCH, TKIND_COCLASS, \
     TKIND_RECORD, TKIND_UNION, TKIND_MODULE, TKIND_ALIAS

from ctypes.com.automation import DISPATCH_METHOD, DISPATCH_PROPERTYGET, \
     DISPATCH_PROPERTYPUT, DISPATCH_PROPERTYPUTREF

from ctypes.com.automation import VAR_PERINSTANCE, VAR_STATIC, VAR_CONST, VAR_DISPATCH

from ctypes.com.automation import IMPLTYPEFLAGS, IMPLTYPEFLAG_FDEFAULT, \
     IMPLTYPEFLAG_FSOURCE, IMPLTYPEFLAG_FRESTRICTED, \
     IMPLTYPEFLAG_FDEFAULTVTABLE

from ctypes.com import GUID
from ctypes import *

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
    VT_VOID: "None",
    VT_HRESULT: "HRESULT", 
    VT_PTR: "VT_PTR",
    VT_LPSTR: "c_char_p",
    VT_LPWSTR: "c_wchar_p",
    }

class TypeInfoReader:
    _order = 0
    def __init__(self, library, typeinfo):
        self.library = library
        self.ti = typeinfo
        # This is used to sort the interfaces later the same way they occurr in the
        # type library.
        self._order = TypeInfoReader._order
        TypeInfoReader._order += 1

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

        if tdesc.vt == VT_VOID:
            return None
        else:
            return TYPES[tdesc.vt]

class EnumReader(TypeInfoReader):
    def declaration(self):
        l = []
        l.append("class %s(c_int):" % self.name)
        if self.docstring:
            l.append('    """%s"""' % self.docstring)
        if self.guid != '{00000000-0000-0000-0000-000000000000}':
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
            oleaut32 = oledll.oleaut32
            oleaut32.VariantChangeType(byref(v),
                                       byref(vsrc),
                                       0, VT_INT)

            self.items.append((name, v._.iVal))
            self.ti.ReleaseVarDesc(pvd)

class RecordReader(TypeInfoReader):
    _baseclass = "Structure"
    def declaration(self):
        l = []
        l.append("class %s(%s):" % (self.name, self._baseclass))
        if self.docstring:
            l.append('    """%s"""' % self.docstring)
        if self.guid != '{00000000-0000-0000-0000-000000000000}':
            l.append("    _iid_ = GUID('%s')" % self.guid)
        l.append("    _fields_ = [")
        for name, value, oInst in self.fields:
            l.append('        (%r, %s),' % (str(name), value))
        l.append("      ]")
        l.append("assert(sizeof(%s) == %d)" % (self.name, self.size))
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

class UnionReader(RecordReader):
    _baseclass = "Union"

class Method:
    def __init__(self, name, restype, argtypes, dispid):
        self.name = name
        self.restype = restype
        self.argtypes = argtypes
        self.dispid = dispid

    def declaration(self):
        items = ['STDMETHOD(%s' % self.restype]
        items.append('"%s"' % self.name)
        items.extend(self.argtypes)
        return ", ".join(items) + ")"


class DispatchMethod(Method):
    # restype is always HRESULT
    def declaration(self):
        items = ['STDMETHOD(HRESULT']
        items.append('"%s"' % self.name)
        items.extend(self.argtypes)
        if self.restype is not None:
            items.append("POINTER(%s)" % self.restype)
        return ", ".join(items) + ")"

class DispMethod(Method):
    def declaration(self):
        items = ['DISPMETHOD(0x%x' % self.dispid]
        if self.restype is not None:
            items.append(self.restype)
        else:
            items.append("None")
        items.append('"%s"' % self.name)
        items.extend(self.argtypes)
        return ", ".join(items) + ")"

class InterfaceReader(TypeInfoReader):
    baseinterface = "IUnknown"
    nummethods = 3
    method_class = Method
    is_dispinterface = 0

    def _parse_typeattr(self, ta):
        assert ta.cImplTypes == 1
        self.wTypeFlags = ta.wTypeFlags
        for i in range(ta.cImplTypes):
            hr = HREFTYPE()
            self.ti.GetRefTypeOfImplType(i, byref(hr))

            ti = pointer(ITypeInfo())
            self.ti.GetRefTypeInfo(hr, byref(ti))

            name = BSTR()
            ti.GetDocumentation(-1, byref(name), None, None, None)
            # XXX Sometimes this fails, because baseinterface is IDispatch
            # in an InterfaceReader 
            if 1:
                self.baseinterface = name.value
            else:
                assert name.value == self.baseinterface, (self, self.baseinterface, name.value)

    def declaration(self):
        l = []
        l.append("class %s(%s):" % (self.name, self.baseinterface))
        if self.docstring:
            l.append('    """%s"""' % self.docstring)
        l.append("    _iid_ = GUID('%s')" % self.guid)
        l.append("")
        return "\n".join(l)

    def _get_methods(self, ta):
        methods = []

        for i in range(ta.cFuncs):
            pfd = LPFUNCDESC()
            self.ti.GetFuncDesc(i, byref(pfd))
            fd = pfd.contents
##            if i < self.nummethods:
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
            mth = self.method_class(name, restype, argtypes, fd.memid)
            methods.append(mth)
            
            self.ti.ReleaseFuncDesc(pfd)
        return methods
    
    def definition(self):
        pta = LPTYPEATTR()
        self.ti.GetTypeAttr(byref(pta))
        ta = pta.contents
        methods = self._get_methods(ta)
        self.ti.ReleaseTypeAttr(pta)

        l = []
        l.append("%s._methods_ = %s._methods_ + [" % (self.name, self.baseinterface))
        for m in methods:
            l.append('    %s,' % m.declaration())
        l.append("]")
        return "\n".join(l)

    def _get_argtypes(self, n, pelemdesc):
        result = []
        for i in range(n):
            e = pelemdesc[i]
            vt = e.tdesc.vt
            result.append(self._get_type(e.tdesc))
        return result

TYPEFLAG_FAPPOBJECT = 0x01
TYPEFLAG_FCANCREATE = 0x02
TYPEFLAG_FLICENSED = 0x04
TYPEFLAG_FPREDECLID = 0x08
TYPEFLAG_FHIDDEN = 0x10
TYPEFLAG_FCONTROL = 0x20
TYPEFLAG_FDUAL = 0x40
TYPEFLAG_FNONEXTENSIBLE = 0x80
TYPEFLAG_FOLEAUTOMATION = 0x100
TYPEFLAG_FRESTRICTED = 0x200
TYPEFLAG_FAGGREGATABLE = 0x400
TYPEFLAG_FREPLACEABLE = 0x800
TYPEFLAG_FDISPATCHABLE = 0x1000
TYPEFLAG_FREVERSEBIND = 0x2000
TYPEFLAG_FPROXY = 0x4000

class DispatchInterfaceReader(InterfaceReader):
    baseinterface = "IDispatch"
    nummethods = 7
    method_class = DispatchMethod

    def _parse_typeattr(self, ta):
        InterfaceReader._parse_typeattr(self, ta)
        if (self.wTypeFlags & TYPEFLAG_FDISPATCHABLE) and not (self.wTypeFlags & TYPEFLAG_FDUAL):
            self.nummethods = 0
            self.method_class = DispMethod
            self.baseinterface = "dispinterface"
            self.is_dispinterface = 1

    def definition(self):
        if not self.is_dispinterface:
            return InterfaceReader.definition(self)
        pta = LPTYPEATTR()
        self.ti.GetTypeAttr(byref(pta))
        ta = pta.contents
        methods = self._get_methods(ta)
        self.ti.ReleaseTypeAttr(pta)

        l = []
        l.append("%s._dispmethods_ = [" % self.name)
        for m in methods:
            l.append('    %s,' % m.declaration())
        l.append("]")
        return "\n".join(l)

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
        l.append("class %s:" % self.name)
        if self.docstring:
            l.append('    """%s"""' % self.docstring)
        l.append("    _reg_clsid_ = %r" % self.guid)

        interfaces = ", ".join(self.interfaces)
        l.append("    _com_interfaces_ = [%s]" % interfaces)

        if self.outgoing_interfaces:
            outgoing = ", ".join(self.outgoing_interfaces)
            l.append("    _outgoing_interfaces_ = [%s]" % outgoing)
        l.append("")
        return "\n".join(l)

HEADER = r"""
###############################################################
# NOTE: This is a GENERATED file. Please do not make changes, #
# they will be overwritten next time it is regenerated.       #
###############################################################

from ctypes import *
from ctypes.com import IUnknown, GUID, STDMETHOD, HRESULT
from ctypes.com.automation import IDispatch, BSTR, VARIANT, \
                                  dispinterface, DISPMETHOD

"""

class TypeLibReader:
    def __init__(self, filename):
        import os
        self.filename = os.path.abspath(filename)
        tlb = self.tlb = LoadTypeLibEx(self.filename)

        self.coclasses = {}
        self.interfaces = {}
        self.enums = []
        self.records = []

        self.types = {}

        for i in range(tlb.GetTypeInfoCount()):
            kind = c_int()
            tlb.GetTypeInfoType(i, byref(kind))
            ti = pointer(ITypeInfo())
            tlb.GetTypeInfo(i, byref(ti))

            # missing:
            # TKIND_ALIAS
            # TKIND_MODULE
            # TKIND_MAX, but this is only a marker

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
                self.enums.append(rdr)
            elif kind.value == TKIND_RECORD:
                rdr = RecordReader(self, ti)
                self.records.append(rdr)
            elif kind.value == TKIND_UNION:
                rdr = UnionReader(self, ti)
                self.records.append(rdr)
                
        for iid in self.types:
            ti = self.types[iid]
            rdr = InterfaceReader(self, ti)
            self.types[iid] = rdr

        self._get_documentation()
        self._get_libattr()

    def _get_libattr(self):
        pta = LPTLIBATTR()
        self.tlb.GetLibAttr(byref(pta))
        ta = pta.contents
        self.guid = str(ta.guid)
        self.wMajorVerNum = ta.wMajorVerNum
        self.wMinorVerNum = ta.wMinorVerNum
        self.wLibFlags = ta.wLibFlags
        self.tlb.ReleaseTLibAttr(pta)

    def _get_documentation(self):
        name = BSTR()
        docstring = BSTR()
        helpcontext = c_ulong()
        helpfile = BSTR()
        self.tlb.GetDocumentation(-1, byref(name),
                                 byref(docstring), byref(helpcontext),
                                 byref(helpfile))
        self.name = name.value
        self.docstring = docstring.value

    def dump(self, ofi=None):

        print >> ofi, "# Generated from %s" % self.filename
        print >> ofi, HEADER

        print >> ofi, "#" * 78
        print >> ofi
        print >> ofi, "# The Type Library"
        print >> ofi, "class %s:" % self.name
        if self.docstring:
            print >> ofi, "    %r" % str(self.docstring)
        print >> ofi, "    guid = GUID('%s')" % self.guid
        print >> ofi, "    version = (%d, %d)" % (self.wMajorVerNum, self.wMinorVerNum)
        print >> ofi, "    flags = 0x%X" % self.wLibFlags
        print >> ofi, "    path = %r" % str(self.filename)
        
        
        if self.enums:
            print >> ofi
            print >> ofi, "#" * 78
            for itf in self.enums:
                print >> ofi
                print >> ofi, itf.declaration()

        if self.records:
            print >> ofi
            print >> ofi, "#" * 78
            for itf in self.records:
                print >> ofi
                print >> ofi, itf.declaration()

        # The following is an attempt to fix problems with a structure
        # containing another structure but it does not work. Probably
        # the simplistic approach to output the datatypes in the same
        # order they appear in the TLB is too naive.
        
##        datatypes = self.enums + self.records
##        if datatypes:
##            print >> ofi
##            print >> ofi, "#" * 78
##            datatypes.sort(lambda a, b: cmp(a._order, b._order))
##            for tp in datatypes:
##                print >> ofi
##                print >> ofi, tp.declaration()

        if self.interfaces:
            print >> ofi
            print >> ofi, "#" * 78
            interfaces = self.interfaces.values()
            # Write out the interfaces in the same order they have appeared
            # in the type lib.
            interfaces.sort(lambda a, b: cmp(a._order, b._order))
            for itf in interfaces:
                print >> ofi
                print >> ofi, itf.declaration()

            for itf in interfaces:
                print >> ofi
                print >> ofi, itf.definition()

        if self.coclasses:
            print >> ofi
            print >> ofi, "#" * 78
            for guid, cls in self.coclasses.iteritems():
                print >> ofi
                print >> ofi, cls.declaration()

def main():
    import sys
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = r"..\samples\server\sum.tlb"
##        path = r"c:\windows\system32\shdocvw.dll"
##        path = r"c:\Programme\Microsoft Office\Office\MSO97.DLL"

        # Microsoft PictureClip Control 6.0 (Ver 1.1)
##        path = r"c:\Windows\System32\PICCLP32.OCX"

    import time
    start = time.clock()
    reader = TypeLibReader(unicode(path))
    stop = time.clock()
    print "# -*- python -*-"
    reader.dump()
    

if __name__ == '__main__':
    main()
