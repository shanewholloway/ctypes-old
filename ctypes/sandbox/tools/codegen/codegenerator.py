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

def _calc_packing(struct, fields, pack, isStruct):
    # Try a certain packing, raise PackingError if field offsets,
    # total size ot total alignment is wrong.
    if struct.size is None: # incomplete struct
        return -1
    if struct.name in dont_assert_size:
        return None
    if struct.bases:
        size = struct.bases[0].size
        total_align = struct.bases[0].align
    else:
        size = 0
        total_align = 8 # in bits
    for i, f in enumerate(fields):
        if f.bits:
##            print "##XXX FIXME"
            return -2 # XXX FIXME
        s, a = storage(f.typ)
        if pack is not None:
            a = min(pack, a)
        if size % a:
            size += a - size % a
        if isStruct:
            if size != f.offset:
                raise PackingError, "field offset (%s/%s)" % (size, f.offset)
            size += s
        else:
            size = max(size, s)
        total_align = max(total_align, a)
    if total_align != struct.align:
        raise PackingError, "total alignment (%s/%s)" % (total_align, struct.align)
    a = total_align
    if pack is not None:
        a = min(pack, a)
    if size % a:
        size += a - size % a
    if size != struct.size:
        raise PackingError, "total size (%s/%s)" % (size, struct.size)

def calc_packing(struct, fields):
    # try several packings, starting with unspecified packing
    isStruct = isinstance(struct, nodes.Structure)
    for pack in [None, 16*8, 8*8, 4*8, 2*8, 1*8]:
        try:
            _calc_packing(struct, fields, pack, isStruct)
        except PackingError, details:
            continue
        else:
            if pack is None:
                return None
            return pack/8
    raise PackingError, "PACKING FAILED: %s" % details

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

# Is this needed?
##renames = {
##    "POINTER(const(WCHAR))": "c_wchar_p",
##    }

##def type_name(t):
##    result = _type_name(t)
##    return renames.get(result, result)

type_name = _type_name

def get_real_type(tp):
    if type(tp) is nodes.Typedef:
        return get_real_type(tp.typ)
    return tp

# XXX These should be filtered out in gccxmlparser.
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
msimg32
rpcrt4""".split()

##rpcndr
##ntdll
##dll_names = "libxml2".split()

from ctypes import CDLL
searched_dlls = [CDLL(name) for name in dll_names]

class Generator(object):
    def __init__(self, stream):
        self.done = set()
        self.stream = stream

    def StructureHead(self, head):
        if head in self.done:
            return
        for struct in head.struct.bases:
            self.StructureHead(struct.get_head())
            self.more.add(struct)
        basenames = [type_name(b) for b in head.struct.bases]
        if basenames:
            print >> self.stream, "class %s(%s):" % (head.struct.name, ", ".join(basenames))
        else:
            methods = [m for m in head.struct.members if type(m) is nodes.Method]
            if methods:
                print >> self.stream, "class %s(_com_interface):" % head.struct.name
            elif type(head.struct) == nodes.Structure:
                print >> self.stream, "class %s(Structure):" % head.struct.name
            elif type(head.struct) == nodes.Union:
                print >> self.stream, "class %s(Union):" % head.struct.name
        print >> self.stream, "    pass"
        self.done.add(head)

    _structures = 0
    def Structure(self, struct):
        if struct in self.done:
            return
        self._structures += 1
        head = struct.get_head()
        self.StructureHead(head)
        body = struct.get_body()
        self.StructureBody(body)
        self.done.add(struct)
        
    _typedefs = 0
    def Typedef(self, tp):
        if tp in self.done:
            return
        self._typedefs += 1
        if type(tp.typ) in (nodes.Structure, nodes.Union):
            self.StructureHead(tp.typ.get_head())
            self.more.add(tp.typ)
        else:
            self.generate(tp.typ)
        if tp.name != type_name(tp.typ):
            print >> self.stream, "%s = %s # typedef" % (tp.name, type_name(tp.typ))
        self.done.add(tp)

    _arraytypes = 0
    def ArrayType(self, tp):
        if tp in self.done:
            return
        self._arraytypes += 1
        self.generate(get_real_type(tp.typ))
        self.generate(tp.typ)
        self.done.add(tp)

    _functiontypes = 0
    def FunctionType(self, tp):
        if tp in self.done:
            return
        self._functiontypes += 1
        self.generate(tp.returns)
        self.generate_all(tp.arguments)
        self.done.add(tp)
        
    _pointertypes = 0
    def PointerType(self, tp):
        if tp in self.done:
            return
        self._pointertypes += 1
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

    _enumtypes = 0
    def Enumeration(self, tp):
        if tp in self.done:
            return
        self._enumtypes += 1
        if tp.name:
            print >> self.stream
            print >> self.stream, "%s = c_int # enum" % tp.name
            for n, v in tp.values:
                print >> self.stream, "%s = %s # enum %s" % (n, v, tp.name)
        else:
            for n, v in tp.values:
                print >> self.stream, "%s = %s # enum" % (n, v)
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
##        if not isinstance(body.struct, nodes.Union) and not methods:
        if not methods:
            pack = calc_packing(body.struct, fields)
            if pack is not None:
                print >> self.stream, "%s._pack_ = %s" % (body.struct.name, pack)
            else:
                print >> self.stream, "# %s" % body.struct.name
        if fields:
            if body.struct.bases:
                assert len(body.struct.bases) == 1
                base = body.struct.bases[0].name
                self.StructureBody(body.struct.bases[0].get_body())
                print >> self.stream, "%s._fields_ = %s._fields_ + [" % (body.struct.name, base)
            else:
                print >> self.stream, "%s._fields_ = [" % body.struct.name
            for f in fields:
                if f.bits is None:
                    print >> self.stream, "    ('%s', %s)," % (f.name, type_name(f.typ))
                else:
                    print >> self.stream, "    ('%s', %s, %s)," % (f.name, type_name(f.typ), f.bits)
            print >> self.stream, "]"
        if methods:
            print >> self.stream, "%s._methods_ = [" % body.struct.name
            for m in methods:
                args = [type_name(a) for a in m.arguments]
                print >> self.stream, "    STDMETHOD(%s, '%s', %s)," % (
                    type_name(m.returns),
                    m.name,
                    ", ".join(args))
            print >> self.stream, "]"
        if body.struct.size and body.struct.name not in dont_assert_size:
            size = body.struct.size // 8
            print >> self.stream, "assert sizeof(%s) == %s, sizeof(%s)" % \
                  (body.struct.name, size, body.struct.name)
            align = body.struct.align // 8
            print >> self.stream, "assert alignment(%s) == %s, alignment(%s)" % \
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
        return "?"

    _functiontypes = 0
    def Function(self, func):
        if func in self.done:
            return
        self._functiontypes += 1
        dllname = self.find_dllname(func.name)
        if dllname and func.extern:
            self.generate(func.returns)
            self.generate_all(func.arguments)
            args = [type_name(a) for a in func.arguments]
            if "__stdcall__" in func.attributes:
                print >> self.stream, "%s = STDCALL('%s', %s, '%s', [%s])" % \
                      (func.name, dllname, type_name(func.returns), func.name, ", ".join(args))
            else:
                print >> self.stream, "%s = CDECL('%s', %s, '%s', [%s])" % \
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

    def generate_code(self, items):
        items = set(items)
        loops = 0
        while items:
            loops += 1
            self.more = set()
            self.generate_all(items)

            items |= self.more
            items -= self.done
        return loops

    def print_stats(self, stream):
        print >> stream, "######################"
        print >> stream, "# Symbols defined:"
        print >> stream, "#"
        print >> stream, "# Struct/Unions: %5d" % self._structures
        print >> stream, "# Functions:     %5d" % self._functiontypes
        print >> stream, "# Enums:         %5d" % self._enumtypes
        print >> stream, "# Typedefs:      %5d" % self._typedefs
        print >> stream, "# Pointertypes:  %5d" % self._pointertypes
        print >> stream, "# Arraytypes:    %5d" % self._arraytypes
        print >> stream, "#"
        total = self._structures + self._functiontypes + self._enumtypes + self._typedefs +\
                self._pointertypes + self._arraytypes
        print >> stream, "# Total symbols: %5d" % total
        print >> stream, "######################"

################################################################

def generate_code(xmlfile, outfile, symbols=None):
    from gccxmlparser import parse
    import sys
    items = parse(xmlfile)

    todo = []

    if symbols:
        syms = set(symbols.split(","))
        for i in items:
            if i.name in syms:
                todo.append(i)
                syms.remove(i.name)

        items = todo
        if syms:
            print "SYMS NOT FOUND", list(syms)

    gen = Generator(outfile)
    # output header
    print >> outfile, "from ctypes import *"
    print >> outfile, "from _support import STDCALL, CDECL"
    print >> outfile, "def const(x): return x"
    print >> outfile
    loops = gen.generate_code(items)
    gen.print_stats(sys.stderr)

    print "needed %d loop(s)" % loops

