# Create ctypes wrapper code for abstract type descriptions.
# Type descriptions are collections of typedesc instances.

import typedesc, sys

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
    if isinstance(t, typedesc.Typedef):
        return storage(t.typ)
    elif isinstance(t, typedesc.ArrayType):
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
    isStruct = isinstance(struct, typedesc.Structure)
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

def type_name(t):
    # Return a string, containing an expression which can be used to
    # refer to the type. Assumes the ctypes.* namespace is available.
    if isinstance(t, typedesc.PointerType):
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
    elif isinstance(t, typedesc.ArrayType):
        return "%s * %s" % (type_name(t.typ), int(t.max)+1)
    elif isinstance(t, typedesc.FunctionType):
        args = map(type_name, [t.returns] + t.arguments)
        if "__stdcall__" in t.attributes:
            return "WINFUNCTYPE(%s)" % ", ".join(args)
        else:
            return "CFUNCTYPE(%s)" % ", ".join(args)
    elif isinstance(t, typedesc.CvQualifiedType):
        # const and volatile are ignored
        return "%s" % type_name(t.typ)
    elif isinstance(t, typedesc.FundamentalType):
        return ctypes_names[t.name]
    elif isinstance(t, typedesc.Structure):
        return t.name
    elif isinstance(t, typedesc.Enumeration):
        if t.name:
            return t.name
        return "c_int" # enums are integers
    elif isinstance(t, typedesc.Typedef):
        return t.name
    return t.name

def decode_value(init):
    # decode init value from gccxml
    if init[0] == "0":
        return int(init, 16) # hex integer
    elif init[0] == "'":
        return eval(init) # character
    elif init[0] == '"':
        return eval(init) # string
    return int(init) # integer

def init_value(t, init):
    tn = type_name(t)
    if tn in ["c_ulonglong", "c_ulong", "c_uint", "c_ushort", "c_ubyte"]:
        return decode_value(init)
    elif tn in ["c_longlong", "c_long", "c_int", "c_short", "c_byte"]:
        return decode_value(init)
    elif tn in ["c_float", "c_double"]:
        return float(init)
    elif tn == "POINTER(c_char)":
        if init[0] == '"':
            value = eval(init)
        else:
            value = int(init, 16)
        return value
    elif tn == "POINTER(c_wchar)":
        if init[0] == '"':
            value = eval(init)
        else:
            value = int(init, 16)
        if isinstance(value, str):
            value = value[:-1] # gccxml outputs "D\000S\000\000" for L"DS"
            value = value.decode("utf-16") # XXX Is this correct?
        return value
    elif tn == "c_void_p":
        if init[0] == "0":
            value = int(init, 16)
        else:
            value = int(init) # hm..
        # Hm, ctypes represents them as SIGNED int
        return value
    elif tn == "c_char":
        return decode_value(init)
    elif tn == "c_wchar":
        value = decode_value(init)
        if isinstance(value, int):
            return unichr(value)
        return value
    elif tn.startswith("POINTER("):
        # Hm, POINTER(HBITMAP__) for example
        return decode_value(init)
    else:
        raise ValueError, "cannot decode %s(%r)" % (tn, init)

def get_real_type(tp):
    if type(tp) is typedesc.Typedef:
        return get_real_type(tp.typ)
    return tp

# XXX These should be filtered out in gccxmlparser.
dont_assert_size = set(
    [
    "__si_class_type_info_pseudo",
    "__class_type_info_pseudo",
    ]
    )

class Generator(object):
    def __init__(self, stream, use_decorators=False):
        self.done = set()
        self.stream = stream
        self.use_decorators = use_decorators

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
            methods = [m for m in head.struct.members if type(m) is typedesc.Method]
            if methods:
                print >> self.stream, "class %s(_com_interface):" % head.struct.name
            elif type(head.struct) == typedesc.Structure:
                print >> self.stream, "class %s(Structure):" % head.struct.name
            elif type(head.struct) == typedesc.Union:
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
        if type(tp.typ) in (typedesc.Structure, typedesc.Union):
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
        if type(tp.typ) is typedesc.PointerType:
            self.PointerType(tp.typ)
        elif type(tp.typ) in (typedesc.Union, typedesc.Structure):
            self.StructureHead(tp.typ.get_head())
            self.more.add(tp.typ)
        elif type(tp.typ) is typedesc.Typedef:
            self.generate(tp.typ)
        else:
            self.generate(tp.typ)
        self.done.add(tp)

    def CvQualifiedType(self, tp):
        if tp in self.done:
            return
        self.generate(tp.typ)
        self.done.add(tp)

    def Variable(self, tp):
        if tp in self.done:
            return
        self.done.add(tp)
        if tp.init is None:
            # wtypes.h contains IID_IProcessInitControl, for example
            return
        try:
            v = init_value(tp.typ, tp.init)
        except (TypeError, ValueError), detail:
            print "Could not init", detail
            return
        print >> self.stream, \
              "%s = %r # %s" % (tp.name,
                                init_value(tp.typ, tp.init),
                                type_name(tp.typ))

    def EnumValue(self, tp):
        if tp in self.done:
            return
        print >> self.stream, \
              "%s = %s # enum %s" % (tp.name, tp.value, tp.enumeration.name or "")
        self.done.add(tp)

    _enumtypes = 0
    def Enumeration(self, tp):
        if tp in self.done:
            return
        self.done.add(tp)
        self._enumtypes += 1
        if tp.name:
            print >> self.stream
            print >> self.stream, "%s = c_int # enum" % tp.name
        for item in tp.values:
            self.EnumValue(item)

    def StructureBody(self, body):
        if body in self.done:
            return
        fields = []
        methods = []
        for m in body.struct.members:
            if type(m) is typedesc.Field:
                fields.append(m)
                if type(m.typ) is typedesc.Typedef:
                    self.generate(get_real_type(m.typ))
                self.generate(m.typ)
            elif type(m) is typedesc.Method:
                methods.append(m)
                self.generate(m.returns)
                self.generate_all(m.arguments)
            elif type(m) is typedesc.Constructor:
                pass

        # we don't need _pack_ on Unions (I hope, at least), and
        # not on COM interfaces:
        #
        # Hm, how to detect a COM interface with no methods? IXMLDOMCDATASection is such a beast...
##        if not isinstance(body.struct, typedesc.Union) and not methods:
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
            print >> self.stream, "%s._fields_ = [" % body.struct.name
            # unnamed fields will get autogenerated names "_", "_1". "_2", "_3", ...
            unnamed_index = 0
            for f in fields:
                if not f.name:
                    if unnamed_index:
                        fieldname = "_%d" % unnamed_index
                    else:
                        fieldname = "_"
                    unnamed_index += 1
                    print >> self.stream, "    # Unnamed field renamed to '%s'" % fieldname
                else:
                    fieldname = f.name
                if f.bits is None:
                    print >> self.stream, "    ('%s', %s)," % (fieldname, type_name(f.typ))
                else:
                    print >> self.stream, "    ('%s', %s, %s)," % (fieldname, type_name(f.typ), f.bits)
            print >> self.stream, "]"
        if methods:
            print >> self.stream, "%s._methods_ = [" % body.struct.name
            for m in methods:
                args = [type_name(a) for a in m.arguments]
                print >> self.stream, "    STDMETHOD(%s, '%s', [%s])," % (
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
        for dll in self.searched_dlls:
            try:
                getattr(dll, name)
            except AttributeError:
                pass
            else:
                return dll._name
##        if self.verbose:
        # warnings.warn, maybe?
##        print >> sys.stderr, "function %s not found in any dll" % name
        return None

    _stdcall_defined = False
    def need_stdcall(self):
        if self._stdcall_defined:
            return
        print >> self.stream, "from ctypes.decorators import stdcall"
        self._stdcall_defined = True

    _cdecl_defined = False
    def need_cdecl(self):
        if self._cdecl_defined:
            return
        print >> self.stream, "from ctypes.decorators import cdecl"
        self._cdecl_defined = True

    _functiontypes = 0
    _notfound_functiontypes = 0
    def Function(self, func):
        if func in self.done:
            return
        dllname = self.find_dllname(func.name)
        if dllname:
            self.generate(func.returns)
            self.generate_all(func.arguments)
            args = [type_name(a) for a in func.arguments]
            if "__stdcall__" in func.attributes:
                self.need_stdcall()
                cc = "stdcall"
            else:
                self.need_cdecl()
                cc = "cdecl"
            print >> self.stream
            if self.use_decorators:
                print >> self.stream, "@ %s(%s, %r, [%s])" % \
                      (cc, type_name(func.returns), dllname, ", ".join(args))
            argnames = ["p%d" % i for i in range(1, 1+len(args))]
            # function definition
            print >> self.stream, "def %s(%s):" % (func.name, ", ".join(argnames))
            print >> self.stream, "    'Function %s in %s'" % (func.name, dllname)
##            print >> self.stream, "    return _api_(%s)" % ", ".join(argnames)
            if not self.use_decorators:
                print >> self.stream, "%s = %s(%s, %r, [%s]) (%s)" % \
                      (func.name, cc, type_name(func.returns), dllname, ", ".join(args), func.name)
            print >> self.stream
            self._functiontypes += 1
        else:
            self._notfound_functiontypes += 1
        self.done.add(func)

    Union = Structure

    def FundamentalType(self, item):
        if item in self.done:
            return
        name = ctypes_names[item.name]
        if name !=  "None":
            print >> self.stream, "from ctypes import %s" % name
        self.done.add(item)

    ########

    def generate(self, item):
        if item in self.done:
            return
        name = getattr(item, "name", None)
        if name in self.known_symbols:
##            print >> self.stream, "# %s is in known_symbols" % name
            print >> self.stream, "from %s import %s" % (self.known_symbols[name].__module__, name)
            self.done.add(item)
            return
        mth = getattr(self, type(item).__name__)
        mth(item)

    def generate_all(self, items):
        for item in items:
            self.generate(item)

    def generate_code(self, items, known_symbols, searched_dlls):
        items = set(items)
        if known_symbols:
            self.known_symbols = known_symbols
        else:
            self.known_symbols = {}
        self.searched_dlls = searched_dlls
        loops = 0
        while items:
            loops += 1
            self.more = set()
            self.generate_all(items)

            items |= self.more
            items -= self.done
        return loops

    def print_stats(self, stream):
        total = self._structures + self._functiontypes + self._enumtypes + self._typedefs +\
                self._pointertypes + self._arraytypes
        print >> stream, "###########################"
        print >> stream, "# Symbols defined:"
        print >> stream, "#"
        print >> stream, "# Struct/Unions:      %5d" % self._structures
        print >> stream, "# Functions:          %5d" % self._functiontypes
        print >> stream, "# Enums:              %5d" % self._enumtypes
        print >> stream, "# Typedefs:           %5d" % self._typedefs
        print >> stream, "# Pointertypes:       %5d" % self._pointertypes
        print >> stream, "# Arraytypes:         %5d" % self._arraytypes
        print >> stream, "# unknown functions:  %5d" % self._notfound_functiontypes
        print >> stream, "#"
        print >> stream, "# Total symbols: %5d" % total
        print >> stream, "###########################"

################################################################

def generate_code(xmlfile,
                  outfile,
                  expressions=None,
                  symbols=None,
                  verbose=False,
                  use_decorators=False,
                  known_symbols=None,
                  searched_dlls=None,
                  types=None):
    # expressions is a sequence of compiled regular expressions,
    # symbols is a sequence of names
    from gccxmlparser import parse
    items = parse(xmlfile)

    todo = []

    if types:
        items = [i for i in items if isinstance(i, types)]
    
    if symbols:
        syms = set(symbols)
        for i in items:
            if i.name in syms:
                todo.append(i)
                syms.remove(i.name)

        if syms:
            print "symbols not found", list(syms)

    if expressions:
        for i in items:
            for s in expressions:
                if i.name is None:
                    continue
                match = s.match(i.name)
                # we only want complete matches
                if match and match.group() == i.name:
                    todo.append(i)
                    break
    if symbols or expressions:
        items = todo

    gen = Generator(outfile, use_decorators=use_decorators)
    # output header
    print >> outfile, "from ctypes import Structure, Union, CFUNCTYPE, WINFUNCTYPE, POINTER"
    print >> outfile, "from ctypes import sizeof, alignment, c_void_p, c_int"
    print >> outfile
    loops = gen.generate_code(items,
                              known_symbols,
                              searched_dlls)
    if verbose:
        gen.print_stats(sys.stderr)
        print >> sys.stderr, "needed %d loop(s)" % loops

