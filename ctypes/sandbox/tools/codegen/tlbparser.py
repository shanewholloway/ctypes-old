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
VARIANT_type = typedesc.Typedef("VARIANT", None) # 128 , 32 ?
# faked COM data types

CURRENCY_type = float_type # wrong
DATE_type = double_type
DECIMAL_type = double_type # wrong - it's a 12 byte structure

COMTYPES = {
    automation.VT_I2: short_type, # 2
    automation.VT_I4: int_type, # 3
    automation.VT_R4: float_type, # 4
    automation.VT_R8: double_type, # 5
    automation.VT_CY: CURRENCY_type, # 6

    automation.VT_DATE: DATE_type, # 7
    automation.VT_BSTR: BSTR_type, # 8

    automation.VT_DISPATCH: PTR(int_type), # 9 XXXX

    automation.VT_ERROR: SCODE_type, # 10
    automation.VT_BOOL: VARIANT_BOOL_type, # 11
    automation.VT_VARIANT: VARIANT_type, # 12
    automation.VT_UNKNOWN: PTR(int_type), # 13 XXX
    automation.VT_DECIMAL: DECIMAL_type, # 14

    automation.VT_I1: char_type, # 16
    automation.VT_UI1: uchar_type, # 17
    automation.VT_UI2: ushort_type, # 18
    automation.VT_UI4: ulong_type, # 19
    automation.VT_I8: longlong_type, # 20
    automation.VT_UI8: ulonglong_type, # 21
    automation.VT_INT: int_type, # 22
    automation.VT_UINT: uint_type, # 23
    automation.VT_VOID: typedesc.Typedef("None", None), # 24
    automation.VT_HRESULT: HRESULT_type, # 25

    automation.VT_SAFEARRAY: typedesc.Typedef("SAFEARRAY", None), # 27

    automation.VT_LPSTR: PTR(char_type), # 30
    automation.VT_LPWSTR: PTR(wchar_t_type), # 31
}

#automation.VT_PTR = 26 # enum VARENUM
#automation.VT_CARRAY = 28 # enum VARENUM
#automation.VT_USERDEFINED = 29 # enum VARENUM

#automation.VT_RECORD = 36 # enum VARENUM

#automation.VT_ARRAY = 8192 # enum VARENUM
#automation.VT_BYREF = 16384 # enum VARENUM

known_symbols = {"VARIANT": "comtypes",
                 "None": "XXX",
                 }

for name in ("comtypes", "ctypes"):
    mod = __import__(name)
    for submodule in name.split(".")[1:]:
        mod = getattr(mod, submodule)
    for name in mod.__dict__:
        known_symbols[name] = mod.__name__

################################################################

class TlbParser(object):

    def __init__(self, path):
        self.tlib = automation.LoadTypeLibEx(path)
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
##            func_doc = tinfo.GetDocumentation(fd.memid)[1]
            assert 0 == fd.cParamsOpt # ?
            returns = self.make_type(fd.elemdescFunc.tdesc, tinfo)

            if fd.callconv == automation.CC_CDECL:
                attributes = "__cdecl__"
            elif fd.callconv == automation.CC_STDCALL:
                attributes = "__stdcall__"
            else:
                raise "NYI", fd.callconv

            func = typedesc.Function(func_name, returns, attributes, extern=1)
            func.dllname = dllname
            self.items[func_name] = func

            for i in range(fd.cParams):
                argtype = self.make_type(fd.lprgelemdescParam[i].tdesc, tinfo)
                func.add_argument(argtype)

        # constants are disabled for now, we need VARIANT
        # functionality to create them, and codegenerator fixes also.
        # But then, constants are not really common in typelibs.
        return

        # constants
        for i in range(ta.cVars):
            vd = tinfo.GetVarDesc(i)
            name = tinfo.GetDocumentation(vd.memid)[0]
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

    # TKIND_INTERFACE = 3
    def ParseInterface(self, tinfo, ta):
        itf_name, doc = tinfo.GetDocumentation(-1)[0:2]
        assert ta.cImplTypes <= 1

        if ta.cImplTypes:
            hr = tinfo.GetRefTypeOfImplType(0)
            tibase = tinfo.GetRefTypeInfo(hr)
            bases = [self.parse_typeinfo(tibase)]
        else:
            bases = []
        members = []
        itf = typedesc.Structure(itf_name,
                                 align=32,
                                 members=members,
                                 bases=bases,
                                 size=32)
        self.items[itf_name] = itf

        assert ta.cVars == 0, "vars on an Interface?"

        for i in range(ta.cFuncs):
            fd = tinfo.GetFuncDesc(i)
            func_name = tinfo.GetDocumentation(fd.memid)[0]
            returns = self.make_type(fd.elemdescFunc.tdesc, tinfo)
            mth = typedesc.Method(func_name, returns)
##            assert fd.cParamsOpt == 0, "optional parameters not yet implemented"
##            print "CUST %s::%s" % (itf_name, func_name),
            for p in range(fd.cParams):
##                print fd.lprgelemdescParam[p]._.paramdesc.wParamFlags,
                typ = self.make_type(fd.lprgelemdescParam[p].tdesc, tinfo)
                mth.add_argument(typ)
##            print
            itf.members.append(mth)

        itf.iid = ta.guid
        return itf

    # TKIND_DISPATCH = 4
    def ParseDispatch(self, tinfo, ta):
        itf_name, doc = tinfo.GetDocumentation(-1)[0:2]
##        print itf_name
        assert ta.cImplTypes == 1

        hr = tinfo.GetRefTypeOfImplType(0)
        tibase = tinfo.GetRefTypeInfo(hr)
        base = self.parse_typeinfo(tibase)
        members = []
        itf = typedesc.DispInterface(itf_name,
                                     members=members,
                                     base=base,
                                     iid=str(ta.guid),
                                     wTypeFlags=ta.wTypeFlags)
        self.items[itf_name] = itf

        flags = ta.wTypeFlags & (automation.TYPEFLAG_FDISPATCHABLE | automation.TYPEFLAG_FDUAL)
        if flags == automation.TYPEFLAG_FDISPATCHABLE:
            # dual interface
            basemethods = 0
        else:
            # pure dispinterface, does only include dispmethods
            basemethods = 7
            assert ta.cFuncs >= 7, "where are the IDispatch methods?"

        assert ta.cVars == 0, "properties on interface not yet implemented"
        for i in range(ta.cVars):
            vd = tinfo.GetVarDesc(i)
##            assert vd.varkind == automation.VAR_DISPATCH
            var_name = tinfo.GetDocumentation(vd.memid)[0]
            print "VAR", itf_name, tinfo.GetDocumentation(vd.memid)[0], vd.varkind
            typ = self.make_type(vd.elemdescVar.tdesc, tinfo)
            mth = typedesc.DispProperty(vd.memid, vd.varkind, var_name, typ)
            itf.members.append(mth)

        for i in range(basemethods, ta.cFuncs):
            fd = tinfo.GetFuncDesc(i)
            func_name = tinfo.GetDocumentation(fd.memid)[0]
            returns = self.make_type(fd.elemdescFunc.tdesc, tinfo)
            names = tinfo.GetNames(fd.memid, fd.cParams+1)
            names.append("rhs")
            names = names[:fd.cParams + 1]
            assert len(names) == fd.cParams + 1
            mth = typedesc.DispMethod(fd.memid, fd.invkind, func_name, returns)
            for p in range(fd.cParams):
                typ = self.make_type(fd.lprgelemdescParam[p].tdesc, tinfo)
                name = names[p+1]
                flags = fd.lprgelemdescParam[p]._.paramdesc.wParamFlags
                if flags & automation.PARAMFLAG_FHASDEFAULT:
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
                mth.add_argument(typ, name, flags, default)
            itf.members.append(mth)

        itf.iid = ta.guid
        return itf
        
    # TKIND_COCLASS = 5

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
        # TKIND_COCLASS = 5
        elif tkind == automation.TKIND_ALIAS: # 6
            return self.ParseAlias(tinfo, ta)
        elif tkind == automation.TKIND_UNION: # 7
            return self.ParseUnion(tinfo, ta)
        else:
##            raise "NYI", tkind
            print "NYI", tkind

    ################################################################

    def parse(self):
        for i in range(self.tlib.GetTypeInfoCount()):
            tinfo = self.tlib.GetTypeInfo(i)
            self.parse_typeinfo(tinfo)
        return self.items

################################################################

def main():
    import sys

    path = r"hnetcfg.dll"
##    path = r"simpdata.tlb"
##    path = r"nscompat.tlb"
##    path = r"mshtml.tlb"
##    path = r"stdole32.tlb"
##    path = r"c:\tss5\include\MeasurementModule.tlb"
##    path = r"c:\tss5\include\fpanel.tlb"
##    path = r"x.tlb"
##    path = r"shdocvw.dll"
    
##    path = r"c:\Programme\Microsoft Office\Office\MSO97.DLL"
##    path = r"c:\Programme\Microsoft Office\Office\MSWORD8.OLB"
##    path = r"msi.dll"
##    path = r"c:\tss5\include\ITDPersist.tlb"

##    path = r"PICCLP32.OCX"
##    path = r"Macromed\Flash\swflash.ocx"
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\win.tlb"
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\win32.tlb"
##    path = r"MSHFLXGD.OCX"
##    path = r"scrrun.dll"
##    path = r"c:\Programme\Gemeinsame Dateien\Microsoft Shared\Speech\sapi.dll"
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\threadapi.tlb"
##    path = r"C:\Dokumente und Einstellungen\thomas\Desktop\tlb\win32.tlb"

##    path = "mytlb.tlb"
    
    p = TlbParser(path)
    items = p.parse()
    from codegenerator import Generator

    gen = Generator(sys.stdout)
    loops = gen.generate_code(items.values(), known_symbols, [])

if __name__ == "__main__":
    main()
