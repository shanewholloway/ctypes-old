from comtypes import automation
import typedesc

################################
def PTR(typ):
    return typedesc.PointerType(typ, 32, 32)

# basic C data types, with size and alingment in bits
char_type = typedesc.FundamentalType("char", 8, 8)
uchar_type = typedesc.FundamentalType("unsigned char", 8, 8)
wchar_t_type = typedesc.FundamentalType("wchar_t", 16, 16)
short_type = typedesc.FundamentalType("short int", 16, 16)
ushort_type = typedesc.FundamentalType("short unsigned int", 16, 16)
int_type = typedesc.FundamentalType("int", 32, 32)
uint_type = typedesc.FundamentalType("unsigned int", 32, 32)
long_type = typedesc.FundamentalType("long int", 32, 32)
ulong_type = typedesc.FundamentalType("long unsigned int", 32, 32)
longlong_type = typedesc.FundamentalType("long long int", 64, 64)
ulonglong_type = typedesc.FundamentalType("long long unsigned int", 64, 64)
float_type = typedesc.FundamentalType("float", 32, 32)
double_type = typedesc.FundamentalType("double", 64, 64)

# basic COM data types
BSTR_type = typedesc.Typedef("BSTR", PTR(wchar_t_type))
SCODE_type = typedesc.Typedef("SCODE", int_type)
VARIANT_BOOL_type = typedesc.Typedef("VARIANT_BOOL", short_type)
HRESULT_type = typedesc.Typedef("HRESULT", ulong_type)

VARIANT_type = typedesc.Structure("VARIANT", align=64, members=[], bases=[], size=128)
IDISPATCH_type = typedesc.Typedef("IDispatch", None)
IUNKNOWN_type = typedesc.Typedef("IUnknown", None)
SAFEARRAY_type = typedesc.Typedef("SAFEARRAY", None)

# faked COM data types
CURRENCY_type = float_type # wrong
DATE_type = double_type # not *that* wrong...
DECIMAL_type = double_type # wrong - it's a 12 byte structure (or was it 16 bytes?)

COMTYPES = {
    automation.VT_I2: short_type, # 2
    automation.VT_I4: int_type, # 3
    automation.VT_R4: float_type, # 4
    automation.VT_R8: double_type, # 5
    automation.VT_CY: CURRENCY_type, # 6
    automation.VT_DATE: DATE_type, # 7
    automation.VT_BSTR: BSTR_type, # 8
    automation.VT_DISPATCH: PTR(IDISPATCH_type), # 9
    automation.VT_ERROR: SCODE_type, # 10
    automation.VT_BOOL: VARIANT_BOOL_type, # 11
    automation.VT_VARIANT: VARIANT_type, # 12
    automation.VT_UNKNOWN: PTR(IUNKNOWN_type), # 13
    automation.VT_DECIMAL: DECIMAL_type, # 14

    automation.VT_I1: char_type, # 16
    automation.VT_UI1: uchar_type, # 17
    automation.VT_UI2: ushort_type, # 18
    automation.VT_UI4: ulong_type, # 19
    automation.VT_I8: longlong_type, # 20
    automation.VT_UI8: ulonglong_type, # 21
    automation.VT_INT: int_type, # 22
    automation.VT_UINT: uint_type, # 23
    automation.VT_VOID: typedesc.FundamentalType("void", 0, 0), # 24
    automation.VT_HRESULT: HRESULT_type, # 25
#automation.VT_PTR = 26 # enum VARENUM
    automation.VT_SAFEARRAY: SAFEARRAY_type, # 27
#automation.VT_CARRAY = 28 # enum VARENUM
    automation.VT_LPSTR: PTR(char_type), # 30
    automation.VT_LPWSTR: PTR(wchar_t_type), # 31
}

#automation.VT_USERDEFINED = 29 # enum VARENUM

#automation.VT_RECORD = 36 # enum VARENUM

#automation.VT_ARRAY = 8192 # enum VARENUM
#automation.VT_BYREF = 16384 # enum VARENUM

################################################################

class TlbParser(object):

    def __init__(self, path):
        self.tlib = automation.LoadTypeLibEx(path, regkind=automation.REGKIND_REGISTER)
        self.items = {}

    def make_type(self, tdesc, tinfo):
        try:
            return COMTYPES[tdesc.vt]
        except KeyError:
            pass

        if tdesc.vt == automation.VT_CARRAY:
            typ = self.make_type(tdesc._.lpadesc[0].tdescElem, tinfo)
            for i in range(tdesc._.lpadesc[0].cDims):
                typ = typedesc.ArrayType(typ,
                                         tdesc._.lpadesc[0].rgbounds[i].lLbound,
                                         tdesc._.lpadesc[0].rgbounds[i].cElements-1)
            return typ

        elif tdesc.vt == automation.VT_PTR:
            typ = self.make_type(tdesc._.lptdesc[0], tinfo)
            return typedesc.PointerType(typ, 32, 32)

        elif tdesc.vt == automation.VT_USERDEFINED:
            ti = tinfo.GetRefTypeInfo(tdesc._.hreftype)
            result = self.parse_typeinfo(ti)
            assert result is not None, ti.GetDocumentation(-1)[0]
            return result

        # VT_SAFEARRAY ???
        raise "NYI", tdesc.vt

    ################################################################

    # TKIND_ENUM = 0
    def ParseEnum(self, tinfo, ta):
        ta = tinfo.GetTypeAttr()
        enum_name, doc, helpcntext, helpfile = tinfo.GetDocumentation(-1)
        enum = typedesc.Enumeration(enum_name, 32, 32)
        self.items[enum_name] = enum

        for i in range(ta.cVars):
            vd = tinfo.GetVarDesc(i)
            name = tinfo.GetDocumentation(vd.memid)[0]
            # XXX should be handled by VARIANT
            assert vd._.lpvarValue[0].n1.n2.vt == automation.VT_I4
            assert vd.varkind == automation.VAR_CONST
            num_val = vd._.lpvarValue[0].n1.n2.n3.iVal
            v = typedesc.EnumValue(name, num_val, enum)
            enum.add_value(v)
        return enum

    # TKIND_RECORD = 1
    def ParseRecord(self, tinfo, ta):
        members = [] # will be filled later
        struct_name, doc, helpcntext, helpfile = tinfo.GetDocumentation(-1)
        struct = typedesc.Structure(struct_name,
                                    align=ta.cbAlignment*8,
                                    members=members,
                                    bases=[],
                                    size=ta.cbSizeInstance*8)
        self.items[struct_name] = struct

        for i in range(ta.cVars):
            vd = tinfo.GetVarDesc(i)
            name = tinfo.GetDocumentation(vd.memid)[0]
            offset = vd._.oInst * 8
            assert vd.varkind == automation.VAR_PERINSTANCE
            typ = self.make_type(vd.elemdescVar.tdesc, tinfo)
            field = typedesc.Field(name,
                                   typ,
                                   None, # bits
                                   offset)
            members.append(field)
        return struct
        
    # TKIND_MODULE = 2
    def ParseModule(self, tinfo, ta):
        assert 0 == ta.cImplTypes
        # functions
        for i in range(ta.cFuncs):
            fd = tinfo.GetFuncDesc(i)
            dllname, func_name, ordinal = tinfo.GetDllEntry(fd.memid, fd.invkind)
            func_doc = tinfo.GetDocumentation(fd.memid)[1]
            assert 0 == fd.cParamsOpt # XXX
            returns = self.make_type(fd.elemdescFunc.tdesc, tinfo)

            if fd.callconv == automation.CC_CDECL:
                attributes = "__cdecl__"
            elif fd.callconv == automation.CC_STDCALL:
                attributes = "__stdcall__"
            else:
                raise "NYI", fd.callconv

            func = typedesc.Function(func_name, returns, attributes, extern=1)
            if func_doc is not None:
                func.doc = str(func_doc)
            func.dllname = dllname
            self.items[func_name] = func

            for i in range(fd.cParams):
                argtype = self.make_type(fd.lprgelemdescParam[i].tdesc, tinfo)
                func.add_argument(argtype)

        # constants
        for i in range(ta.cVars):
            vd = tinfo.GetVarDesc(i)
            name, var_doc = tinfo.GetDocumentation(vd.memid)[0:2]
            vt = vd._.lpvarValue[0].n1.n2.vt
            assert vd.varkind == automation.VAR_CONST
            # XXX Should be handled by VARIANT
            if vt == automation.VT_I4:
                typ = self.make_type(vd.elemdescVar.tdesc, tinfo)
                num_val = vd._.lpvarValue[0].n1.n2.n3.iVal
                v = typedesc.Variable(name, typ, repr(num_val))
                self.items[name] = v
            elif vt == automation.VT_BSTR:
                typ = self.make_type(vd.elemdescVar.tdesc, tinfo)
                str_val = vd._.lpvarValue[0].n1.n2.n3.bstrVal
                v = typedesc.Variable(name, typ, '''"%s"''' % str_val)
                self.items[name] = v
            else:
                print "VT", vt
            if var_doc is not None:
                v.doc = var_doc

    # TKIND_INTERFACE = 3
    def ParseInterface(self, tinfo, ta):
        itf_name, doc = tinfo.GetDocumentation(-1)[0:2]
        assert ta.cImplTypes <= 1

        if ta.cImplTypes:
            hr = tinfo.GetRefTypeOfImplType(0)
            tibase = tinfo.GetRefTypeInfo(hr)
            base = self.parse_typeinfo(tibase)
        else:
            base = None
        members = []
        itf = typedesc.ComInterface(itf_name,
                                    members=members,
                                    base=base,
                                    iid=str(ta.guid),
                                    idlflags=self.idl_flags(ta.wTypeFlags))
        self.items[itf_name] = itf

        assert ta.cVars == 0, "vars on an Interface?"

        for i in range(ta.cFuncs):
            fd = tinfo.GetFuncDesc(i)
            func_name = tinfo.GetDocumentation(fd.memid)[0]
            returns = self.make_type(fd.elemdescFunc.tdesc, tinfo)
            names = tinfo.GetNames(fd.memid, fd.cParams+1)
            names.append("rhs")
            names = names[:fd.cParams + 1]
            assert len(names) == fd.cParams + 1
            flags = self.func_flags(fd.wFuncFlags)
            flags += self.inv_kind(fd.invkind)
            mth = typedesc.ComMethod(fd.invkind, func_name, returns, flags)
            for p in range(fd.cParams):
                typ = self.make_type(fd.lprgelemdescParam[p].tdesc, tinfo)
                name = names[p+1]
                flags = fd.lprgelemdescParam[p]._.paramdesc.wParamFlags
                if flags & automation.PARAMFLAG_FHASDEFAULT:
                    # XXX should be handled by VARIANT itself
                    var = fd.lprgelemdescParam[p]._.paramdesc.pparamdescex[0].varDefaultValue
                    if var.n1.n2.vt == automation.VT_BSTR:
                        default = var.n1.n2.n3.bstrVal
                    elif var.n1.n2.vt == automation.VT_I4:
                        default = var.n1.n2.n3.iVal
                    elif var.n1.n2.vt == automation.VT_BOOL:
                        default = bool(var.n1.n2.n3.boolVal)
                    else:
                        raise "NYI", var.n1.n2.vt
                else:
                    default = None
                mth.add_argument(typ, name, self.param_flags(flags), default)
            itf.members.append(mth)

        return itf

    # TKIND_DISPATCH = 4
    def ParseDispatch(self, tinfo, ta):
        itf_name, doc = tinfo.GetDocumentation(-1)[0:2]
        assert ta.cImplTypes == 1

        hr = tinfo.GetRefTypeOfImplType(0)
        tibase = tinfo.GetRefTypeInfo(hr)
        base = self.parse_typeinfo(tibase)
        members = []
        itf = typedesc.DispInterface(itf_name,
                                     members=members,
                                     base=base,
                                     iid=str(ta.guid),
                                     idlflags=self.idl_flags(ta.wTypeFlags))
        itf.doc = str(doc)
        self.items[itf_name] = itf

        flags = ta.wTypeFlags & (automation.TYPEFLAG_FDISPATCHABLE | automation.TYPEFLAG_FDUAL)
        if flags == automation.TYPEFLAG_FDISPATCHABLE:
            # dual interface
            basemethods = 0
        else:
            # pure dispinterface, does only include dispmethods
            basemethods = 7
            assert ta.cFuncs >= 7, "where are the IDispatch methods?"

        for i in range(ta.cVars):
            vd = tinfo.GetVarDesc(i)
            assert vd.varkind == automation.VAR_DISPATCH
            var_name, doc = tinfo.GetDocumentation(vd.memid)[0:2]
            typ = self.make_type(vd.elemdescVar.tdesc, tinfo)
            mth = typedesc.DispProperty(vd.memid, var_name, typ, self.var_flags(vd.wVarFlags))
            mth.doc = str(doc)
            itf.members.append(mth)

        for i in range(basemethods, ta.cFuncs):
            fd = tinfo.GetFuncDesc(i)
            func_name = tinfo.GetDocumentation(fd.memid)[0]
            returns = self.make_type(fd.elemdescFunc.tdesc, tinfo)
            names = tinfo.GetNames(fd.memid, fd.cParams+1)
            names.append("rhs")
            names = names[:fd.cParams + 1]
            assert len(names) == fd.cParams + 1 # function name first, then parameter names
            flags = self.func_flags(fd.wFuncFlags)
            flags += self.inv_kind(fd.invkind)
            mth = typedesc.DispMethod(fd.memid, fd.invkind, func_name, returns, flags)
            doc = tinfo.GetDocumentation(fd.memid)[1]
            if doc is not None:
                mth.doc = str(doc)
            for p in range(fd.cParams):
                typ = self.make_type(fd.lprgelemdescParam[p].tdesc, tinfo)
                name = names[p+1]
                flags = fd.lprgelemdescParam[p]._.paramdesc.wParamFlags
                if flags & automation.PARAMFLAG_FHASDEFAULT:
                    # XXX should be handled by VARIANT itself
                    var = fd.lprgelemdescParam[p]._.paramdesc.pparamdescex[0].varDefaultValue
                    if var.n1.n2.vt == automation.VT_BSTR:
                        default = var.n1.n2.n3.bstrVal
                    elif var.n1.n2.vt == automation.VT_I4:
                        default = var.n1.n2.n3.iVal
                    elif var.n1.n2.vt == automation.VT_BOOL:
                        default = bool(var.n1.n2.n3.boolVal)
                    elif var.n1.n2.vt == automation.VT_R4:
                        default = var.n1.n2.n3.fltVal
                    else:
                        raise "NYI", var.n1.n2.vt
                else:
                    default = None
                mth.add_argument(typ, name, self.param_flags(flags), default)
            itf.members.append(mth)

        return itf

    def inv_kind(self, invkind):
        NAMES = {automation.DISPATCH_METHOD: [],
                 automation.DISPATCH_PROPERTYPUT: ["propput"],
                 automation.DISPATCH_PROPERTYPUTREF: ["propputref"],
                 automation.DISPATCH_PROPERTYGET: ["propget"]}
        return NAMES[invkind]

    def func_flags(self, flags):
        # map FUNCFLAGS values to idl attributes
        NAMES = {automation.FUNCFLAG_FRESTRICTED: "restricted",
                 automation.FUNCFLAG_FSOURCE: "source",
                 automation.FUNCFLAG_FBINDABLE: "bindable",
                 automation.FUNCFLAG_FREQUESTEDIT: "requestedit",
                 automation.FUNCFLAG_FDISPLAYBIND: "displaybind",
                 automation.FUNCFLAG_FDEFAULTBIND: "defaultbind",
                 automation.FUNCFLAG_FHIDDEN: "hidden",
                 automation.FUNCFLAG_FUSESGETLASTERROR: "usesgetlasterror",
                 automation.FUNCFLAG_FDEFAULTCOLLELEM: "defaultcollelem",
                 automation.FUNCFLAG_FUIDEFAULT: "uidefault",
                 automation.FUNCFLAG_FNONBROWSABLE: "nonbrowsable",
                 # automation.FUNCFLAG_FREPLACEABLE: "???",
                 automation.FUNCFLAG_FIMMEDIATEBIND: "immediatebind"}
        return [NAMES[bit] for bit in NAMES if bit & flags]
                 
    def param_flags(self, flags):
        # map PARAMFLAGS values to idl attributes
        NAMES = {automation.PARAMFLAG_FIN: "in",
                 automation.PARAMFLAG_FOUT: "out",
                 automation.PARAMFLAG_FLCID: "lcid",
                 automation.PARAMFLAG_FRETVAL: "retval",
                 automation.PARAMFLAG_FOPT: "optional",
                 # automation.PARAMFLAG_FHASDEFAULT: "",
                 # automation.PARAMFLAG_FHASCUSTDATA: "",
                 }
        return [NAMES[bit] for bit in NAMES if bit & flags]

    def idl_flags(self, flags):
        # map TYPEFLAGS values to idl attributes
        NAMES = {automation.TYPEFLAG_FAPPOBJECT: "appobject",
                 # automation.TYPEFLAG_FCANCREATE:
                 automation.TYPEFLAG_FLICENSED: "licensed",
                 # automation.TYPEFLAG_FPREDECLID:
                 automation.TYPEFLAG_FHIDDEN: "hidden",
                 automation.TYPEFLAG_FCONTROL: "control",
                 automation.TYPEFLAG_FDUAL: "dual",
                 automation.TYPEFLAG_FNONEXTENSIBLE: "nonextensible",
                 automation.TYPEFLAG_FOLEAUTOMATION: "oleautomation",
                 automation.TYPEFLAG_FRESTRICTED: "restricted",
                 automation.TYPEFLAG_FAGGREGATABLE: "aggregatable",
                 # automation.TYPEFLAG_FREPLACEABLE:
                 # automation.TYPEFLAG_FDISPATCHABLE # computed, no flag for this
                 automation.TYPEFLAG_FREVERSEBIND: "reversebind",
                 automation.TYPEFLAG_FPROXY: "proxy",
                 }
        return [NAMES[bit] for bit in NAMES if bit & flags]
    
    def var_flags(self, flags):
        NAMES = {automation.VARFLAG_FREADONLY: "readonly",
                 automation.VARFLAG_FSOURCE: "source",
                 automation.VARFLAG_FBINDABLE: "bindable",
                 automation.VARFLAG_FREQUESTEDIT: "requestedit",
                 automation.VARFLAG_FDISPLAYBIND: "displaybind",
                 automation.VARFLAG_FDEFAULTBIND: "defaultbind",
                 automation.VARFLAG_FHIDDEN: "hidden",
                 automation.VARFLAG_FRESTRICTED: "restricted",
                 automation.VARFLAG_FDEFAULTCOLLELEM: "defaultcollelem",
                 automation.VARFLAG_FUIDEFAULT: "uidefault",
                 automation.VARFLAG_FNONBROWSABLE: "nonbrowsable",
                 automation.VARFLAG_FREPLACEABLE: "replaceable",
                 automation.VARFLAG_FIMMEDIATEBIND: "immediatebind"
                 }
        return [NAMES[bit] for bit in NAMES if bit & flags]
    

    # TKIND_COCLASS = 5
    def ParseCoClass(self, tinfo, ta):
        # possible ta.wTypeFlags: helpstring, helpcontext, licensed,
        #        version, control, hidden, and appobject
        coclass_name, doc = tinfo.GetDocumentation(-1)[0:2]
        coclass = typedesc.CoClass(coclass_name, str(ta.guid), self.idl_flags(ta.wTypeFlags))
        if doc is not None:
            coclass.doc = str(doc)
        self.items[coclass_name] = coclass
        for i in range(ta.cImplTypes):
            hr = tinfo.GetRefTypeOfImplType(i)
            ti = tinfo.GetRefTypeInfo(hr)
            itf = self.parse_typeinfo(ti)
            flags = tinfo.GetImplTypeFlags(i)
            coclass.add_interface(itf, flags)
        return coclass

    # TKIND_ALIAS = 6
    def ParseAlias(self, tinfo, ta):
        name = tinfo.GetDocumentation(-1)[0]
        typ = self.make_type(ta.tdescAlias, tinfo)
        alias = typedesc.Typedef(name, typ)
        self.items[name] = alias
        return alias
    
    # TKIND_UNION = 7
    def ParseUnion(self, tinfo, ta):
        union_name, doc, helpcntext, helpfile = tinfo.GetDocumentation(-1)
        members = []
        union = typedesc.Union(union_name,
                               align=ta.cbAlignment*8,
                               members=members,
                               bases=[],
                               size=ta.cbSizeInstance*8)
        self.items[union_name] = union

        for i in range(ta.cVars):
            vd = tinfo.GetVarDesc(i)
            name = tinfo.GetDocumentation(vd.memid)[0]
            offset = vd._.oInst * 8
            assert vd.varkind == automation.VAR_PERINSTANCE
            typ = self.make_type(vd.elemdescVar.tdesc, tinfo)
            field = typedesc.Field(name,
                                   typ,
                                   None, # bits
                                   offset)
            members.append(field)
        return union
        
    ################################################################

    def parse_typeinfo(self, tinfo):
        name = tinfo.GetDocumentation(-1)[0]
        try:
            return self.items[name]
        except KeyError:
            pass
        ta = tinfo.GetTypeAttr()
        tkind = ta.typekind
        if tkind == automation.TKIND_ENUM: # 0
            return self.ParseEnum(tinfo, ta)
        elif tkind == automation.TKIND_RECORD: # 1
            return self.ParseRecord(tinfo, ta)
        elif tkind == automation.TKIND_MODULE: # 2
            return self.ParseModule(tinfo, ta)
        elif tkind == automation.TKIND_INTERFACE: # 3
            return self.ParseInterface(tinfo, ta)
        elif tkind == automation.TKIND_DISPATCH: # 4
            return self.ParseDispatch(tinfo, ta)
        elif tkind == automation.TKIND_COCLASS: # 5
            return self.ParseCoClass(tinfo, ta)
        elif tkind == automation.TKIND_ALIAS: # 6
            return self.ParseAlias(tinfo, ta)
        elif tkind == automation.TKIND_UNION: # 7
            return self.ParseUnion(tinfo, ta)
        else:
            raise "NYI", tkind

    ################################################################

    def parse(self):
        for i in range(self.tlib.GetTypeInfoCount()):
            tinfo = self.tlib.GetTypeInfo(i)
            self.parse_typeinfo(tinfo)
        return self.items

################################################################

coclass = typedesc.FundamentalType("CoClass", 32, 32) # fake for codegen

def main():
    import sys

##    path = r"hnetcfg.dll"
##    path = r"simpdata.tlb"
##    path = r"nscompat.tlb"
##    path = r"mshtml.tlb"
##    path = r"stdole32.tlb"
##    path = "msscript.ocx"
##    path = r"shdocvw.dll"
    
##    path = r"c:\Programme\Microsoft Office\Office\MSO97.DLL"
##    path = r"c:\Programme\Microsoft Office\Office\MSWORD8.OLB"
##    path = r"msi.dll" # DispProperty

##    path = r"PICCLP32.OCX" # DispProperty
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\win.tlb"
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\win32.tlb"
##    path = r"MSHFLXGD.OCX"
##    path = r"scrrun.dll"
##    path = r"c:\Programme\Gemeinsame Dateien\Microsoft Shared\Speech\sapi.dll"
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\threadapi.tlb"
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\win32.tlb"

##    path = "mytlb.tlb"
##    # this has a IUnknown* default parameter
##    path = r"c:\Programme\Gemeinsame Dateien\Microsoft Shared\Speech\sapi.dll"
    
##    path = r"c:\tss5\include\fpanel.tlb"
    path = "auto.tlb"
    known_symbols = {}

    for name in ("comtypes.automation", "comtypes", "ctypes"):
        mod = __import__(name)
        for submodule in name.split(".")[1:]:
            mod = getattr(mod, submodule)
        for name in mod.__dict__:
            known_symbols[name] = mod.__name__

    p = TlbParser(path)
    items = p.parse()
    items["CoClass"] = coclass
    from codegenerator import Generator

    gen = Generator(sys.stdout)
    print >> gen.imports, "from helpers import *"
    loops = gen.generate_code(items.values(), known_symbols, [])

if __name__ == "__main__":
    main()
