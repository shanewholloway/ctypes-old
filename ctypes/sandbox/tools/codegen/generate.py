import nodes
from ctypes_names import ctypes_names

try:
    set
except NameError:
    from sets import Set as set

################

##renames = {}
class Generator(object):
    def __init__(self):
        self.done = set()

    def type_name(self, t):
        # Return a string, containing an expression which can be used to
        # refer to the type. Assumes the ctypes.* namespace is available.
        if isinstance(t, nodes.PointerType):
            result = "POINTER(%s)" % self.type_name(t.typ)
            # XXX Better to inspect t.typ!
            if result.startswith("POINTER(WINFUNCTYPE"):
                return result[8:-1]
            # XXX See comment above...
            elif result == "POINTER(None)":
                return "c_void_p"
            return result
        elif isinstance(t, nodes.ArrayType):
            return "%s * %s" % (self.type_name(t.typ), int(t.max)+1)
        elif isinstance(t, nodes.FunctionType):
            args = map(self.type_name, [t.returns] + t.arguments)
            # what now?  WINFUNCTYPE already *is* a pointer to a function
            return "WINFUNCTYPE(%s)" % ", ".join(args)
        elif isinstance(t, nodes.CvQualifiedType):
            return "c_const(%s)" % self.type_name(t.typ)
        elif isinstance(t, nodes.FundamentalType):
            return ctypes_names[t.name]
        elif isinstance(t, nodes.Structure):
##            try:
##                return renames[t]
##            except KeyError:
                return t.name
        elif isinstance(t, nodes.Enumeration):
##            try:
##                return renames[t]
##            except KeyError:
##                pass
            if t.name:
                return t.name
            return "c_int" # enums are integers
        return t.name
    
    def Enumeration(self, enum):
        if enum.name is not None:
            # enums are integers (AFAIK, but may depend on the compiler)
            print "%s = c_int" % enum.name
        for name, val in enum.values:
            print "%s = %s" % (name, val)
        print

    def Typedef(self, t):
        print "%s = %s" % (t.name, self.type_name(t.typ))

    def StructureHead(self, t):
        assert t.struct.name is not None
        print "class %s(Structure):" % t.struct.name
        print "    pass"

    def StructureBody(self, t):
        self.done.update(t.struct.members)
        fields = [m for m in t.struct.members if type(m) is nodes.Field]
        if fields:
            print "%s._fields_ = [" % t.struct.name
            for m in fields:
                if m.bits:
                    print "    ('%s', %s, %s)," % (m.name, self.type_name(m.typ), m.bits)
                else:
                    print "    ('%s', %s)," % (m.name, self.type_name(m.typ))
            print "]"

        methods = [m for m in t.struct.members if type(m) is nodes.Method]
        if methods:
            print "%s._methods_ = [" % t.struct.name
            for m in methods:
                args = [self.type_name(a) for a in m.arguments]
                text = "    STDMETHOD(%s, '%s'" % (self.type_name(m.returns), m.name)
                if args:
                    print "%s, %s)," % (text, ", ".join(args))
                else:
                    print "%s)," % text
            print "]"
        
    def Function(self, t):
        if not t.extern:
            return
        dllname = "<unknown>"
        if "__stdcall__" in t.attributes:
            print "%s = STDCALL(%r, %s, '%s', %s)" % \
                  (t.name, dllname, self.type_name(t.returns),
                   t.name, ", ".join(map(self.type_name, t.arguments)))
        else: # __cdecl is default
            print "%s = CDECL(%r, %s, '%s', %s)" % \
                  (t.name, dllname, self.type_name(t.returns),
                   t.name, ", ".join(map(self.type_name, t.arguments)))

    def _generate(self, t):
        # the dispatcher
        typ = type(t)
        if typ is nodes.Enumeration:
            self.Enumeration(t)
        elif typ is nodes.Typedef:
            self.Typedef(t)
        elif typ is nodes.StructureHead:
            self.StructureHead(t)
        elif typ is nodes.StructureBody:
            self.StructureBody(t)
        elif typ is nodes.Function:
            self.Function(t)
        elif typ in (nodes.Structure, nodes.Union,
                     nodes.PointerType, nodes.FundamentalType,
                     nodes.ArrayType, nodes.FunctionType):
            self.done.add(t)
        else:
            raise TypeError, "don't know how to generate code for %s" % t
        self.done.add(t)
    
    def generate(self, items):
        todo = set(items)
        # todo contains definitions we have to generate
        # self.done contains definitions already done

        for i in range(80):
            for td in todo.copy():
                if type(td) is nodes.PointerType \
                       and type(td.typ) in (nodes.Structure, nodes.Union):
                    # pointers to struct or union only depend on their head,
                    # but we want the body as well.
                    #
                    # XXX Maybe it would be better to have this in the
                    # code generator for the struct/union head.
                    todo.add(td.typ)
                needs = set(td.depends())
                assert td not in needs
                if needs.issubset(self.done):
                    self._generate(td)
                    assert td in self.done
                else:
                    todo.update(needs)
            todo -= self.done
            if not todo:
                return
        if todo:
            raise "Not enough loops???", (len(todo), todo)

################################################################

def find_names(names):
    from gccxmlparser import parse
    items = parse(files=["windows.h"], xmlfile="windows.xml")

    result = []
    for i in items:
        if getattr(i, "name", None) in names:
            result.append(i)
    return result

def main():
    items = find_names(sys.argv[1:])
    gen = Generator()
    print "from ctypes import *"
    print "def STDMETHOD(*args): pass"
    print "def c_const(x): return x"
    gen.generate(items)

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        sys.argv.extend("IDispatch".split())
    main()
