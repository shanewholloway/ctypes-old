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
        return "c_const(%s)" % type_name(t.typ)
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
            if type(head.struct) == nodes.Structure:
                print "class %s(Structure):" % head.struct.name
            elif type(head.struct) == nodes.Union:
                print "class %s(Union):" % head.struct.name
        print "    pass"
        self.done.add(head)

    def Structure(self, struct):
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
            self.generate([tp.typ])
        print "%s = %s" % (tp.name, type_name(tp.typ))
        self.done.add(tp)

    def ArrayType(self, tp):
        if tp in self.done:
            return
        if type(tp.typ) is nodes.Typedef:
            self.more.add(tp.typ)
        self.generate([get_real_type(tp.typ)])
        self.done.add(tp)

    def FunctionType(self, tp):
        if tp in self.done:
            return
        self.generate([tp.returns])
        self.generate(tp.arguments)
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
            self.generate([tp.typ])
        else:
            self.generate([tp.typ])
        self.done.add(tp)

    def CvQualifiedType(self, tp):
        if tp in self.done:
            return
        self.generate([tp.typ])
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
                self.generate([get_real_type(m.typ)])
                if getattr(t, "name", None) == "SIZE":
                    import pdb
                    pdb.set_trace()
                if type(t) in (nodes.Structure, nodes.Union):
                    assert t.get_body() in self.done
                
##                self.generate([m.typ])
            elif type(m) is nodes.Method:
                methods.append(m)
                self.generate([m.returns])
                self.generate(m.arguments)
            elif type(m) is nodes.Constructor:
                pass
        if fields:
            print "%s._fields_ = [" % body.struct.name
            for f in fields:
                print "    ('%s', %s)," % (f.name, type_name(f.typ))
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
        self.done.add(body)

    def Function(self, func):
        if func in self.done:
            return
        if func.extern:
            self.generate([func.returns])
            self.generate(func.arguments)
            args = [type_name(a) for a in func.arguments]
            if "__stdcall__" in func.attributes:
                print "STDCALL(%s, '%s', %s)" % \
                      (type_name(func.returns), func.name, ", ".join(args))
            else:
                print "CDECL(%s, '%s', %s)" % \
                      (type_name(func.returns), func.name, ", ".join(args))
        self.done.add(func)

    def generate(self, items):
        for item in items:
            tp = type(item)
            if tp in (nodes.Structure, nodes.Union):
                self.Structure(item)
            elif tp == nodes.Typedef:
                self.Typedef(item)
            elif tp == nodes.FundamentalType:
                pass
            elif tp == nodes.PointerType:
                self.PointerType(item)
            elif tp == nodes.CvQualifiedType:
                self.CvQualifiedType(item)
            elif tp == nodes.ArrayType:
                self.ArrayType(item)
            elif tp == nodes.Enumeration:
                self.Enumeration(item)
            elif tp == nodes.StructureHead:
                self.StructureHead(item)
            elif tp == nodes.FunctionType:
                self.FunctionType(item)
            elif tp == nodes.Function:
                self.Function(item)
            else:
                raise "NYI", tp

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
    from gccxmlparser import parse
##    items = parse(files=["windows.h"], xmlfile="windows.xml")
    items = find_names(sys.argv[1:])
    gen = Generator()
    print "from ctypes import *"
    print "def STDMETHOD(*args): pass"
    print "def c_const(x): return x"
    print

    for i in range(20):
        gen.more = set()
        gen.generate(items)
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
        sys.argv.extend("IDispatch".split())
##        sys.argv.extend("ITypeComp".split())
    main()
