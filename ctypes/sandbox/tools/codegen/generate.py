import nodes
from ctypes_names import ctypes_names

try:
    set
except NameError:
    from sets import Set as set

################

def type_name(t):
    # Return a string, containing an expression which can be used to
    # refer to the type. Assumes the ctypes.* namespace is available.
    if isinstance(t, nodes.PointerType):
        result = "POINTER(%s)" % type_name(t.typ)
        # XXX Better to inspect t.typ!
        if result.startswith("POINTER(WINFUNCTYPE"):
            return result[8:-1]
        # XXX See comment above...
        elif result == "POINTER(None)":
            return "c_void_p"
        return result
    elif isinstance(t, nodes.ArrayType):
        return "%s * %s" % (type_name(t.typ), int(t.max)+1)
    elif isinstance(t, nodes.FunctionType):
        args = map(type_name, [t.returns] + t.arguments)
        # what now?  WINFUNCTYPE already *is* a pointer to a function
        return "WINFUNCTYPE(%s)" % ", ".join(args)
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
        return type_name(get_real_type(t.typ))
    return t.name

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
            print "%s = %s" % (tp.name, type_name(tp.typ))
        self.done.add(tp)

    def ArrayType(self, tp):
        if tp in self.done:
            return
        if type(tp.typ) is nodes.Typedef:
            self.more.add(tp.typ)
        self.generate(get_real_type(tp.typ))
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
            print "%s = c_int" % tp.name
        for n, v in tp.values:
            print "%s = %s" % (n, v)
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
                    self.more.add(m.typ)
                t = get_real_type(m.typ)
                self.generate(get_real_type(m.typ))
                if type(t) in (nodes.Structure, nodes.Union):
                    assert t.get_body() in self.done
                
            elif type(m) is nodes.Method:
                methods.append(m)
                self.generate(m.returns)
                self.generate_all(m.arguments)
            elif type(m) is nodes.Constructor:
                pass
        try:
            pack = struct_packing[body.struct.name]
        except KeyError:
            pass
        else:
            print "%s._pack_ = %s" % (body.struct.name, pack)
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
        self.done.add(body)

    def find_dllname(self, name):
        for dll in searched_dlls:
            try:
                getattr(dll, name)
            except AttributeError:
                pass
            else:
                return dll._name
        return None

    def Function(self, func):
        if func in self.done:
            return
        if func.name == "qsort":
            import pdb
            pdb.set_trace()
        dllname = self.find_dllname(func.name)
        if dllname and func.extern:
            self.generate(func.returns)
            self.generate_all(func.arguments)
            args = [type_name(a) for a in func.arguments]
            if "__stdcall__" in func.attributes:
                print "%s = STDCALL('%s', %s, '%s', (%s))" % \
                      (func.name, dllname, type_name(func.returns), func.name, ", ".join(args))
            else:
                print "%s = CDECL('%s', %s, '%s', (%s))" % \
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
    items = parse(files=["windows.h"], xmlfile="windows.xml", options=["-D _WIN32_WINNT=0x500"])

    if "*" in names:
        return items

    result = []
    for i in items:
        if getattr(i, "name", None) in names:
            result.append(i)
    return result

def main():
    from gccxmlparser import parse
##    items = parse(files=["windows.h"], xmlfile="windows.xml")
    items = find_names(sys.argv[1:])
    gen = Generator()
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
        sys.argv.extend("MessageBox".split())
##        sys.argv.extend("ITypeComp".split())
    main()
