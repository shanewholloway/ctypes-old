# bugs:
# packing of derived structures (assertion error at build time)
# packing of unions (assertion errors at import time of generated module)
# bitfields?

import nodes

try:
    set
except NameError:
    from sets import Set as set

# XXX Should this be in ctypes itself?
ctypes_names = {
    "unsigned char": "c_ubyte",
    "signed char": "c_byte",
    "char": "c_char",

    "wchar_t": "c_wchar",

    "short unsigned int": "c_ushort",
    "short int": "c_short",

    "long unsigned int": "c_ulong",
    "long int": "c_long",
    "long signed int": "c_long",

    "unsigned int": "c_uint",
    "int": "c_int",

    "long long unsigned int": "c_ulonglong",
    "long long int": "c_longlong",

    "double": "c_double",
    "float": "c_float",

    # Hm...
    "void": "None",
}

################

def storage(t):
    # return the size and alignment of a type
    if isinstance(t, nodes.Typedef):
        return storage(t.typ)
    elif isinstance(t, nodes.ArrayType):
        s, a = storage(t.typ)
        return s * (int(t.max) - int(t.min) + 1), a
    return int(t.size), int(t.align)

class PackingError(Exception):
    pass

def _calc_packing(struct, fields, pack, verbose):
    if struct.size is None: # incomplete struct
        return -1
    if struct.name in dont_assert_size:
        return None
    assert not isinstance(struct, nodes.Union)
    if struct.bases:
        size = struct.bases[0].size
    else:
        size = 0
    total_align = 8 # in bits
    for i, f in enumerate(fields):
        if f.bits:
            return -2
        s, a = storage(f.typ)
        if pack is not None:
            a = min(pack, a)
        if size % a:
            size += a - size % a
        if size != int(f.offset):
            raise PackingError, "field offset"
        size += s
        total_align = max(total_align, a)
    if total_align != struct.align:
        raise PackingError, "total alignment (%s/%s)" % (total_align / 8, struct.align)
    a = total_align
    if pack is not None:
        a = min(pack, a)
    if size % a:
        size += a - size % a
    if size != struct.size:
        raise PackingError, "total size"

def calc_packing(struct, fields, verbose=False):
    # try several packings, starting with unspecified packing
    for pack in [None, 16*8, 8*8, 4*8, 2*8, 1*8]:
        try:
            _calc_packing(struct, fields, pack, verbose)
        except PackingError:
            continue
        else:
            if pack is None:
                return None
            return pack/8
##    assert 0, "PACKING FAILED"
    print "##WARNING: Packing failed", struct.size

def _type_name(t):
    # Return a string, containing an expression which can be used to
    # refer to the type. Assumes the ctypes.* namespace is available.
    if isinstance(t, nodes.PointerType):
        result = "POINTER(%s)" % type_name(t.typ)
        # XXX Better to inspect t.typ!
        if result.startswith("POINTER(WINFUNCTYPE"):
            return result[8:-1]
        if result.startswith("POINTER(CFUNCTYPE"):
            return result[8:-1]
        # XXX See comment above...
        elif result == "POINTER(None)":
            return "c_void_p"
        return result
    elif isinstance(t, nodes.ArrayType):
        return "%s * %s" % (type_name(t.typ), int(t.max)+1)
    elif isinstance(t, nodes.FunctionType):
        args = map(type_name, [t.returns] + t.arguments)
        # WINFUNCTYPE already *is* a pointer to a function!
        return "CFUNCTYPE(%s)" % ", ".join(args)
    elif isinstance(t, nodes.CvQualifiedType):
        return "const(%s)" % type_name(t.typ)
    elif isinstance(t, nodes.FundamentalType):
        return ctypes_names[t.name]
    elif isinstance(t, nodes.Structure):
        return t.name
    elif isinstance(t, nodes.Enumeration):
        if t.name:
            return t.name
        return "c_int" # enums are integers
    elif isinstance(t, nodes.Typedef):
        return t.name
    return t.name

renames = {
##    "POINTER(const(WCHAR))": "c_wchar_p",
    }

def type_name(t):
    result = _type_name(t)
    return renames.get(result, result)

def get_real_type(tp):
    if type(tp) is nodes.Typedef:
        return get_real_type(tp.typ)
    return tp

struct_packing = {
    "_IMAGE_SYMBOL": 2,
    "tagPDA": 2,
    "tagPDW": 2,
    "DLGITEMTEMPLATE": 2,
    "tWAVEFORMATEX": 2,
    "DLGTEMPLATE": 2,
    "tagMETAHEADER": 2,
    "tagBITMAPFILEHEADER": 2,

    "_SHQUERYRBINFO": 4,

    "waveformat_tag": 2,
    "_py_N17_IMAGE_AUX_SYMBOL4__26E": 2,
    "_IMAGE_AUX_SYMBOL": 2,
    "IMAGE_AUX_SYMBOL_TOKEN_DEF": 2,
    "_IMAGE_LINENUMBER": 2,
    "_IMAGE_RELOCATION": 2,

    "_SHFILEOPSTRUCTW": 2,
    "_SHFILEOPSTRUCTA": 2,

    "_SENDCMDOUTPARAMS": 1,
    "_SENDCMDINPARAMS": 1,
    }

dont_assert_size = set(
    [
    "__si_class_type_info_pseudo",
    "__class_type_info_pseudo",
    ]
    )

dll_names = """\
user32
kernel32
gdi32
advapi32
oleaut32
ole32
imm32
comdlg32
shell32
version
winmm
mpr
winscard
winspool.drv
urlmon
crypt32
cryptnet
ws2_32
opengl32
mswsock
msvcrt
rpcrt4""".split()

##rpcndr
##ntdll
##dll_names = "libxml2".split()

from ctypes import CDLL
searched_dlls = [CDLL(name) for name in dll_names]

class Generator(object):
    def __init__(self):
        self.done = set()
        self.more = set()

    def StructureHead(self, head):
        if head in self.done:
            return
        for struct in head.struct.bases:
            self.StructureHead(struct.get_head())
            self.more.add(struct)
        basenames = [type_name(b) for b in head.struct.bases]
        if basenames:
            print "class %s(%s):" % (head.struct.name, ", ".join(basenames))
        else:
            methods = [m for m in head.struct.members if type(m) is nodes.Method]
            if methods:
                print "class %s(_com_interface):" % head.struct.name
            elif type(head.struct) == nodes.Structure:
                print "class %s(Structure):" % head.struct.name
            elif type(head.struct) == nodes.Union:
                print "class %s(Union):" % head.struct.name
        print "    pass"
        self.done.add(head)

    def Structure(self, struct):
        if struct in self.done:
            return
        head = struct.get_head()
        self.StructureHead(head)
        body = struct.get_body()
        self.StructureBody(body)
        self.done.add(struct)
        
    def Typedef(self, tp):
        if tp in self.done:
            return
        if type(tp.typ) in (nodes.Structure, nodes.Union):
            self.StructureHead(tp.typ.get_head())
            self.more.add(tp.typ)
        else:
            self.generate(tp.typ)
        if tp.name != type_name(tp.typ):
            print "%s = %s # typedef" % (tp.name, type_name(tp.typ))
        self.done.add(tp)

    def ArrayType(self, tp):
        if tp in self.done:
            return
        self.generate(get_real_type(tp.typ))
        self.generate(tp.typ)
        self.done.add(tp)

    def FunctionType(self, tp):
        if tp in self.done:
            return
        self.generate(tp.returns)
        self.generate_all(tp.arguments)
        self.done.add(tp)
        
    def PointerType(self, tp):
        if tp in self.done:
            return
        if type(tp.typ) is nodes.PointerType:
            self.PointerType(tp.typ)
        elif type(tp.typ) in (nodes.Union, nodes.Structure):
            self.StructureHead(tp.typ.get_head())
            self.more.add(tp.typ)
        elif type(tp.typ) is nodes.Typedef:
            self.generate(tp.typ)
        else:
            self.generate(tp.typ)
        self.done.add(tp)

    def CvQualifiedType(self, tp):
        if tp in self.done:
            return
        self.generate(tp.typ)
        self.done.add(tp)

    def Enumeration(self, tp):
        if tp in self.done:
            return
        if tp.name:
            print
            print "%s = c_int # enum" % tp.name
            for n, v in tp.values:
                print "%s = %s # enum %s" % (n, v, tp.name)
        else:
            for n, v in tp.values:
                print "%s = %s # enum" % (n, v)
        self.done.add(tp)

    def StructureBody(self, body):
        if body in self.done:
            return
        fields = []
        methods = []
        for m in body.struct.members:
            if type(m) is nodes.Field:
                fields.append(m)
                if type(m.typ) is nodes.Typedef:
                    self.generate(get_real_type(m.typ))
                self.generate(m.typ)
            elif type(m) is nodes.Method:
                methods.append(m)
                self.generate(m.returns)
                self.generate_all(m.arguments)
            elif type(m) is nodes.Constructor:
                pass

        # we don't need _pack_ on Unions (I hope, at least), and
        # not on COM interfaces:
        #
        # Hm, how to detect a COM interface with no methods? IXMLDOMCDATASection is such a beast...
        if not isinstance(body.struct, nodes.Union) and not methods:
            pack = calc_packing(body.struct, fields)
            if pack is not None:
                print "%s._pack_ = %s" % (body.struct.name, pack)
            else:
                print "# %s" % body.struct.name
        if fields:
            if body.struct.bases:
                assert len(body.struct.bases) == 1
                base = body.struct.bases[0].name
                self.StructureBody(body.struct.bases[0].get_body())
                print "%s._fields_ = %s._fields_ + [" % (body.struct.name, base)
            else:
                print "%s._fields_ = [" % body.struct.name
            for f in fields:
                if f.bits is None:
                    print "    ('%s', %s)," % (f.name, type_name(f.typ))
                else:
                    print "    ('%s', %s, %s)," % (f.name, type_name(f.typ), f.bits)
            print "]"
        if methods:
            print "%s._methods_ = [" % body.struct.name
            for m in methods:
                args = [type_name(a) for a in m.arguments]
                print "    STDMETHOD(%s, '%s', %s)," % (
                    type_name(m.returns),
                    m.name,
                    ", ".join(args))
            print "]"
        if body.struct.size and body.struct.name not in dont_assert_size:
            size = body.struct.size // 8
            print "assert sizeof(%s) == %s, sizeof(%s)" % \
                  (body.struct.name, size, body.struct.name)
            align = body.struct.align // 8
            print "assert alignment(%s) == %s, alignment(%s)" % \
                  (body.struct.name, align, body.struct.name)
        self.done.add(body)

    def find_dllname(self, name):
        for dll in searched_dlls:
            try:
                getattr(dll, name)
            except AttributeError:
                pass
            else:
                return dll._name
##        return None
        return "?"

    def Function(self, func):
        if func in self.done:
            return
        dllname = self.find_dllname(func.name)
        if dllname and func.extern:
            self.generate(func.returns)
            self.generate_all(func.arguments)
            args = [type_name(a) for a in func.arguments]
            if "__stdcall__" in func.attributes:
                print "%s = STDCALL('%s', %s, '%s', [%s])" % \
                      (func.name, dllname, type_name(func.returns), func.name, ", ".join(args))
            else:
                print "%s = CDECL('%s', %s, '%s', [%s])" % \
                      (func.name, dllname, type_name(func.returns), func.name, ", ".join(args))
        self.done.add(func)

    Union = Structure

    def FundamentalType(self, item):
        self.done.add(item)

    ########

    def generate(self, item):
        mth = getattr(self, type(item).__name__)
        mth(item)

    def generate_all(self, items):
        for item in items:
            self.generate(item)

################################################################

def find_names(names):
    from gccxmlparser import parse
    items = parse(files=["windows.h"],
                  options=["-D WIN32_LEAN_AND_MEAN"],
##                  options=["-dM"],
                  xmlfile="windows.xml")

    if "*" in names:
        return items

    result = []
    for i in items:
        if getattr(i, "name", None) in names:
            result.append(i)
    return result

def main():
##    items = parse(files=["windows.h"], xmlfile="windows.xml")
    items = find_names(sys.argv[1:])
    gen = Generator()
    print "# files='windows.h'"
    print "# options='-D WIN32_LEAN_AND_MEAN'"
    print "from ctypes import *"
    print "from _support import STDMETHOD, const, STDCALL, CDECL, _com_interface"
##    print "def STDMETHOD(*args): pass"
##    print "def const(x): return x"
##    print "STDCALL = CDECL = STDMETHOD"
##    print "class _com_interface(Structure):"
##    print "    _fields_ = [('lpVtbl', c_void_p)]"
    print

    for i in range(20):
        gen.more = set()
        gen.generate_all(items)
        items = gen.more
        if not items:
            break
    if items:
        print "left after 20 loops", len(items)
        import pdb
        pdb.set_trace()

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        sys.argv.extend("*")
#        sys.argv.extend("WNDCLASS".split())
##        sys.argv.extend("ITypeComp".split())
    main()
