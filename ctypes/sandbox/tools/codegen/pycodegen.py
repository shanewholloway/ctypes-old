import nodes
from ctypes_names import ctypes_names

try:
    set
except NameError:
    from sets import Set as set

################

renames = {}

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
        return "c_const(%s)" % type_name(t.typ)
    elif isinstance(t, nodes.FundamentalType):
        return ctypes_names[t.name]
    elif isinstance(t, nodes.Structure):
        try:
            return renames[t]
        except KeyError:
            return t.name
    elif isinstance(t, nodes.Enumeration):
        try:
            return renames[t]
        except KeyError:
            pass
        if t.name:
            return t.name
        return "c_int" # enums are integers
    return t.name
    
def make_enum(name, enum):
    if name is not None:
        # enums are integers (AFAIK, but may depend on the compiler)
        print "%s = c_int" % name
    for name, val in enum.values:
        print "%s = %s" % (name, val)
    print

def make_struct_header(name, struct, isStruct):
    methods = [m for m in struct.members if isinstance(m, nodes.Method)]
    if struct.bases:
        bases = [type_name(b) for b in struct.bases]
    elif methods: # a com interface
        bases = "_com_interface_base",
    elif isStruct:
        bases = "Structure",
    else:
        bases = "Union",
    if isStruct:
        print "class %s(%s):" % (name, ", ".join(bases))
    else:
        print "class %s(%s):" % (name, ", ".join(bases))
    print "    pass"

def make_struct_body(name, struct):
    methods = [m for m in struct.members if isinstance(m, nodes.Method)]
    fields = [m for m in struct.members if isinstance(m, nodes.Field)]
    if fields:
        if struct.bases:
            print "%s._fields_ = %s._fields_ + [" % (name, base_name)
        else:
            print "%s._fields_ = [" % name
        for m in fields:
            if m.bits:
                print "    ('%s', %s, %s)," % (m.name, type_name(m.typ), m.bits)
            else:
                print "    ('%s', %s)," % (m.name, type_name(m.typ))
        print "]"
    else:
        if methods:
            pass
        elif struct.bases: # ???
            pass
##            print "%s._fields_ = %s._fields_ + [" % (name, type_name(struct.bases[0]))            
        else:
            print "%s._fields_ = []" % name

    if methods:
        if struct.bases:
            print "%s._methods_ = %s._methods_ + [" % (name, type_name(struct.bases[0]))
        else:
            print "%s._methods_ = [" % name
        for m in methods:
            args = [type_name(a) for a in m.arguments]
            text = "    STDMETHOD(%s, '%s'" % (type_name(m.returns), m.name)
            if args:
                print "%s, %s)," % (text, ", ".join(args))
            else:
                print "%s)," % text
        print "]"

    try:
        size = int(struct.size)
    except TypeError:
        pass
    else:
        print "assert sizeof(%s) == %s" % (name, size/8)
    print

################

def gen_enums(done, items):
    # generate Python code for enums
    enums = []

    for i in items:
        if isinstance(i, nodes.Typedef) and isinstance(i.typ, nodes.Enumeration):
            comment = "#typedef enum %s %s;" % (i.typ.name or "<unnamed>", i.name)
            if i.typ.name:
                renames[i.typ.name] = i.name
                renames[i.typ] = i.name
            enums.append((i.name, comment, i.name, i.typ))
            done.add(i)
            done.add(i.typ)

    for i in items - done:
        if isinstance(i, nodes.Enumeration):
            comment = "#enum %s;" % i.name
            enums.append((i.name, comment, None, i))
            done.add(i)

    enums.sort()

    for name, comment, enum_name, typ in enums:
        print comment
        make_enum(enum_name, typ)

    return done, items - done

def gen_structs(done, items):
##    bodies = []
    structs = []
    for i in items:
        if isinstance(i, nodes.Typedef) and isinstance(i.typ, (nodes.Structure, nodes.Union)):
            print "#typedef struct %s %s;" % (i.typ.name or "<unnamed>", i.name)
            if i.typ.name:
##                renames[i.typ.name] = i.name
                renames[i.typ] = i.name
            isStruct = isinstance(i.typ, nodes.Structure)
            make_struct_header(i.name, i.typ, isStruct)
##            bodies.append((i.name, i.typ))
            done.add(i)
            done.add(i.typ)

    for i in items - done:
        if isinstance(i, (nodes.Structure, nodes.Union)):
            if i.name is None:
                continue # internal structure?
            print "#typedef struct %s;" % i.name
            isStruct = isinstance(i, nodes.Structure)
            make_struct_header(i.name, i, isStruct)
##            bodies.append((i.name, i))
            done.add(i)

    for i in items - done:
        if isinstance(i, nodes.StructureHead):
            print "#typedef struct %s;" % i.struct.name
            isStruct = isinstance(i, nodes.Structure)
            make_struct_header(i.struct.name, i.struct, True)
            done.add(i)

    return done, items - done

def get_pointed_to(p):
    # if p is a pointer, return the end of the chain pointed to.
    if isinstance(p, nodes.PointerType):
        return get_pointed_to(p.typ)
    elif isinstance(p, nodes.CvQualifiedType):
        return get_pointed_to(p.typ)
    return p

def gen_typedefs(done, items):
    for i in items:
        if isinstance(i, nodes.FundamentalType):
            done.add(i)
    for i in items - done:
        if isinstance(i, nodes.Typedef):
            tp_name = type_name(i.typ)
            if tp_name != i.name:
                print "%s = %s" % (i.name, type_name(i.typ))
            done.add(i)

    for i in items - done:
        if not isinstance(i, nodes.Typedef):
            continue
        if i.typ in done:
            print "%s = %s #" % (i.name, type_name(i.typ))
            done.add(i)
        elif isinstance(i.typ, nodes.PointerType) and get_pointed_to(i.typ) in done:
            print "%s = %s ##" % (i.name, type_name(i.typ))
            done.add(i)
    return done, items - done

def gen_arrays(done, items):
    for i in items:
        if isinstance(i, nodes.ArrayType):
            done.add(i)
    return done, items - done

from ctypes import windll, cdll
# do we also want ntdll.dll?
dllnames = """netapi32 scarddlg comctl32 mswsock mpr version opengl32 cryptnet
comdlg32 shell32 winscard winspool.drv urlmon winmm imm32 user32
kernel32 advapi32 gdi32 ws2_32 rpcrt4 rpcns4 ole32 oleaut32 crypt32
msvcrt"""

dlls = [getattr(cdll, name) for name in dllnames.split()]

def find_dll(funcname):
    for l in dlls:
        try:
            getattr(l, funcname)
        except AttributeError:
            pass
        else:
            return l._name
    return None

def gen_functions(done, items):
    for i in items:
        if not isinstance(i, nodes.Function):
            continue
        if not i.extern:
            done.add(i)
            continue
        dllname = find_dll(i.name)
        if dllname is None:
            dllname = "<unknown>"
        if "__stdcall__" in i.attributes:
            print "%s = STDCALL(%r, %s, '%s', %s)" % \
                  (i.name, dllname, type_name(i.returns),
                   i.name, ", ".join(map(type_name, i.arguments)))
        else: # __cdecl is default
            print "%s = CDECL(%r, %s, '%s', %s)" % \
                  (i.name, dllname, type_name(i.returns),
                   i.name, ", ".join(map(type_name, i.arguments)))
        done.add(i)
    return done, items - done

################

def main_old():
    from gccxmlparser import parse
    items = parse(files=["windows.h"], xmlfile="windows.xml")
    items = set(items)

    print "# pass 1", len(items)
    done = set()
    done, items = gen_enums(done, items)
    print "# pass 2", len(items)
    done, items = gen_typedefs(done, items)
    print "# pass 3", len(items)
    done, items = gen_structs(done, items)
    print "# pass 4", len(items)
    done, items = gen_typedefs(done, items)
    print "# pass 5", len(items)
    done, items = gen_functions(done, items)
    print "# pass 6", len(items)
    items = list(items)
    import pdb
    pdb.set_trace()

def generate(item):
    done = set()
    items = set([item])
    done, items = gen_enums(done, items)
    done, items = gen_typedefs(done, items)
    done, items = gen_arrays(done, items)
    done, items = gen_structs(done, items)
    done, items = gen_functions(done, items)
    if type(item) is nodes.StructureBody:
        make_struct_body(item.struct.name, item.struct)
        done.add(item)
##    assert done, "no code generated for %s" % item
    return done

################################################################

def find(names, fname=None):
    if fname:
        import cPickle
        items = cPickle.loads(open(fname, "rb").read())
    else:
        from gccxmlparser import parse
        items = parse(files=["windows.h"], xmlfile="windows.xml", verbose=1)

        print "# creating pickle..",
        import cPickle
        data = cPickle.dumps(items)
        open("windows.pickle", "wb").write(data)
        print "done"

    print "# searching...",
    result = []
    for i in items:
        if getattr(i, "name", None) in names:
            result.append(i)
    print "done"
    return result

def depends(i):
    deps = i.depends()
    result = set()
    for x in deps:
        if not isinstance(x, nodes.FundamentalType):
            result.add(x)
    return result
            

def main():
    done = set()
    todo = set()

    import sys
##    todo.update(find(sys.argv[1:], "windows.pickle"))
    todo.update(find(sys.argv[1:]))

    print "from ctypes import *"
    print "def c_const(x): return x"
    print "def STDCALL(*x): return x"
    print "STDMETHOD = STDCALL"
    print "def CDECL(*x): return x"
    print "class _com_interface_base(Structure):"
    print "    _fields_ = [('lpVtbl', c_void_p)]"
    print

    for howoften in range(200):
        for i in todo.copy():
            needs = set(i.depends())
            assert i not in needs
            if needs.issubset(done): # can generate this one now
##                print "# generate", i
##                print "#depends", i.depends()
                if type(i) in (nodes.Structure, nodes.Union):
                    todo.add(i.get_body())
                a = generate(i)
                done.update(a)
                done.add(i)
            else:
                todo.update(needs)
##                print i
        todo -= done
##        print "#%d:" % howoften, len(done), len(todo)
        if not todo:
            print "# done after %d iterations" % howoften
            return list(todo), list(done)
    todo = list(todo)
    print "# left %d items after %d iterations" % (len(todo), howoften+1)
    print "#", todo
    return todo, list(done)

def explain(t, done):
    needs = t.depends()
    unresolved = set(done) - set(needs)
    print "for type", t
    print "unresolved", unresolved

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        sys.argv.append("IDispatch")
    todo, done = main()
##    if todo:
##        print explain(todo[0], done)

# TODO-List:
#
# separate dependencies between structure body and structure fields,
# so that the various IType... interfaces can be generated.
#
# calculate/guess Structure alignment
#
# read IID's from the registry (?)
