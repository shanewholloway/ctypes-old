# Create ctypes python wrapper for everything in windows.h.
# '#define' preprocessor statements are *not* handled - this will be a
# separate effort.
#
# Bugs:
#  Structure packing is wrong (gccxml doesn't handle the #pragma statements)
#
# COM interfaces are not included, so structures and unions containing
# pointers to COM interfaces will not be generated (VARIANT, for example)
#
# enums are generated as subclasses of c_int, with the enum values as
# class variables.  This should probably change.
#
# Unnamed structure fields will probably not work correctly.
#
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
            print "# resolved %d of %d -> %d" % (len(resolved), len(remaining),
                                                 len(remaining) - len(resolved))
            if not resolved:
                print "# %d unresolved deps" % len(remaining)
                return result, remaining
            done = done | resolved
            remaining = remaining - resolved
        return result, list(remaining)

################################################################

HEADER = """\
from ctypes import *

IUnknown = c_void_p
IDispatch = c_void_p
IRecordInfo = c_void_p
"""

class CodeGenerator(gccxmltools.Visitor):

    def __init__(self):
        self._env = {}
        self.try_code(HEADER)

    def PointerType(self, ptr):
        pass

    def Enumeration(self, enum):
        # generate the ctypes code for an enumeration.
        code = ["class %s(c_int):" % enum.name]
        code += ["    %s = %s" % pair for pair in enum.values]
        self.try_code(code)

    def Typedef(self, td):
        if type(td.typ) is gccxmltools.Structure and td.typ.isClass():
            return
        code = "%s = %s" % (td.name, self.ctypes_name(td.typ))
        self.try_code(code)

    def Structure(self, struct):
        code = self.gen_structure(struct)
        if struct.name.startswith("$_"):
            return
        self.try_code(code)

    Union = Structure

    def gen_structure(self, struct, indent=""):
        # create inner classes
        base = struct.__class__.__name__
        inner = []
        name = struct.name
        if name.startswith("$_"):
            name = "_inner_" + name[2:]
        for field in struct.members:
            if type(field.typ) in (gccxmltools.Structure, gccxmltools.Union) \
                   and field.typ.name.startswith("$_"):
                inner.append(field.typ)
        code = [indent + "class %s(%s):" % (name, base)]
        for i in inner:
            code += self.gen_structure(i, indent = indent + "    ")
        code += [indent + "    _fields_ = ["]
        code += [indent + "        ('%s', %s)," % self.gen_member(f) for f in struct.members]
        code += [indent + "    ]"]
        return code

    def gen_member(self, field):
        name = field.name
        if name.startswith("$_"):
            name = "_inner_" + name[2:]
        return name, self.ctypes_name(field.typ)

    def try_code(self, code):
        # code it either a string or a sequence of strings
        if isinstance(code, (str, unicode)):
            text = code
        else:
            text = "\n".join(code)
        try:
            exec text in self._env
        except Exception, details:
            print "# --- %s: %s ---" % (details.__class__.__name__, details)
            print "##" + "\n##".join(text.splitlines())
        else:
            print text

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
        elif type(obj) in (gccxmltools.Typedef, gccxmltools.Enumeration, \
                           gccxmltools.Structure, gccxmltools.Union):
            name = obj.name
            if obj.name.startswith("$_"):
                name = "_inner_" + name[2:]
            return name
        raise TypeError, type(obj)

################################################################

if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
##        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windef.h".split())
        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windows.h".split())

    result = gccxmltools.main()

    p = DependencyResolver(result)
    resolved, unresolved = p.run()

##    cg = CodeGenerator(result)
##    cg.go()

##    for o in remaining:
##        print "#", o

    cg = CodeGenerator()
    cg.go(resolved)
    print
    print "################################################################"
    print
    cg.go(unresolved)

