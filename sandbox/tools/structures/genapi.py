import gccxmltools
from sets import Set

ctypes_names = {
    "char": "c_char",
    "unsigned char": "c_ubyte",

    "wchar_t": "c_wchar",

    "short int": "c_short",
    "short unsigned int": "c_ushort",

    "int": "c_int",
    "unsigned int": "c_uint",

    "long int": "c_long",
    "long unsigned int": "c_ulong",

    "long long int": "c_longlong",
    "long long unsigned int": "c_ulonglong",

    "void": "void",
    
    "double": "c_double",
    "float": "c_float",
    }

class DependencyResolver(object):
    def __init__(self, objects):
        self.__objects = objects

    def run(self):
        # returns a tuple of two lists.  The first one contains
        # objects for which to generate code, the second contains
        # objects with unresolved dependencies.
        result = []
        done = Set()
        remaining = Set()

        for o in self.__objects:
            # ONLY THOSE THAT WE DON'T NEED ANYWAY
            if type(o) is gccxmltools.Structure and o.isClass():
                done.add(o)
            elif type(o) is gccxmltools.Constructor:
                done.add(o)
            elif type(o) is gccxmltools.FundamentalType:
                done.add(o)
            elif type(o) is gccxmltools.FunctionType:
                done.add(o)
            elif type(o) is gccxmltools.Function:
                done.add(o)
            elif type(o) is gccxmltools.Method:
                done.add(o)
            else:
                remaining.add(o)

        while remaining:
            resolved = Set()
            for o in remaining:
                deps = Set(o.depends())
                if not deps - done:
                    resolved.add(o)
                    result.append(o)
            print "# resolved %d of %d -> %d" % (len(resolved), len(remaining), len(remaining) - len(resolved))
            if not resolved:
                print "# %d unresolved deps" % len(remaining)
                return result, remaining
            done = done | resolved
            remaining = remaining - resolved
        return result, list(remaining)

################################################################

class CodeGenerator(gccxmltools.Visitor):

    def __init__(self, *args, **kw):
        super(CodeGenerator, self).__init__(*args, **kw)
        self._env = {}
        exec "from ctypes import *" in self._env

    def Enumeration(self, enum):
        # generate the ctypes code for an enumeration.
        code = ["class %s(c_int):" % enum.name]
        code += ["    %s = %s" % pair for pair in enum.values]
        code = "\n".join(code)
        exec code in self._env
        print code

    def Typedef(self, td):
        if type(td.typ) is gccxmltools.Structure and td.typ.isClass():
            return
        code = "%s = %s" % (td.name, self.ctypes_name(td.typ))
        try:
            exec code in self._env
        except Exception:
            print "#", code
        else:
            print code

    def Structure(self, struct):
        if struct.name.startswith("$_"):
            return
        code = ["class %s(Structure):" % struct.name]
        code += ["    _fields_ = []"]
        try:
            exec "\n".join(code) in self._env
        except Exception:
            print "#", code[0]
        else:
            print "\n".join(code)

    Union = Structure

    def ctypes_name(self, obj):
        if type(obj) is gccxmltools.FundamentalType:
            return ctypes_names[obj.name]
        elif type(obj) is gccxmltools.FunctionType:
            return "c_void_p" # fixme
        elif type(obj) is gccxmltools.PointerType:
            name = self.ctypes_name(obj.typ)
            if name == "void":
                return "c_void_p"
            return "POINTER(%s)" % name
        elif type(obj) is gccxmltools.CvQualifiedType:
            return self.ctypes_name(obj.typ)
        elif type(obj) is gccxmltools.ArrayType:
            assert obj.min == 0
            return "%s * %d" % (self.ctypes_name(obj.typ), obj.max + 1)
        elif type(obj) in (gccxmltools.Typedef, gccxmltools.Enumeration, gccxmltools.Structure, gccxmltools.Union):
            return obj.name
        raise TypeError, type(obj)

################################################################

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windef.h".split())
##        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windows.h".split())

    result = gccxmltools.main()

    p = DependencyResolver(result)
    result, remaining = p.run()

    print "from ctypes import *"
    print

    cg = CodeGenerator(result)
    cg.go()

    for o in remaining:
        print "#", o
