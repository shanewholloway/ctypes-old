import os, re
from gccxmlparser import parse
import typedesc


# C keywords, according to MSDN, plus some additional
# names like __forceinline, near, far.

# Skip all definitions where the rhs is a keyword
# Example: #define CALLBACK __stdcall
#
# Hm, should types be handled differently?
# Example: #define VOID void
C_KEYWORDS = """__asm else main struct __assume enum
__multiple_inheritance switch auto __except __single_inheritance
template __based explicit __virtual_inheritance this bool extern
mutable thread break false naked throw case __fastcall namespace true
catch __finally new try __cdecl float noreturn __try char for operator
typedef class friend private typeid const goto protected typename
const_cast if public union continue inline register unsigned
__declspec __inline default int return uuid delete __int8 short
__uuidof dllexport __int16 signed virtual dllimport __int32 sizeof
void do __int64 static volatile double __leave static_cast wmain
dynamic_cast long __stdcall while far near __forceinline __w64
__noop""".split()

"""
PROPSHEETPAGEA_V1_FIELDS
PROPSHEETPAGEW_V1_FIELDS
"""

# defines we know that won't work
EXCLUDED = """\
NOTIFYICONDATAA_V1_SIZE
NOTIFYICONDATAA_V2_SIZE
PROPSHEETHEADERA_V1_SIZE
PROPSHEETHEADERA_V2_SIZE
PROPSHEETHEADERW_V2_SIZE
NOTIFYICONDATAW_V2_SIZE
s_imp
s_host
s_lh
s_net
s_addr
h_addr
s_impno
_VARIANT_BOOL
MIDL_uhyper
WINSCARDDATA
__MIDL_DECLSPEC_DLLIMPORT
__MIDL_DECLSPEC_DLLEXPORT
NCB_POST
STDAPI
STDAPIV
WINAPI
SHDOCAPI
WINOLEAUTAPI
WINOLEAPI
APIENTRY
EXTERN_C
FIRMWARE_PTR
STDMETHODIMPV
STDMETHODIMP
REFCLSID
REFFMTID
REFIID
DEFAULT_UNREACHABLE
MAXLONGLONG
IMAGE_ORDINAL_FLAG64
SECURITY_NT_AUTHORITY
FMTID_NULL
IID_NULL
CLSID_NULL
ANONYMOUS_LOGON_LUID
SYSTEM_LUID
LOCALSERVICE_LUID
SECURITY_RESOURCE_MANAGER_AUTHORITY
SECURITY_NULL_SID_AUTHORITY
SECURITY_CREATOR_SID_AUTHORITY
SECURITY_WORLD_SID_AUTHORITY
SECURITY_LOCAL_SID_AUTHORITY
SECURITY_NON_UNIQUE_AUTHORITY
NETWORKSERVICE_LUID
REFGUID""".split()

log = open("skipped.txt", "w")

wordpat = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")

def _gccxml_get_defines(fname=None):
    cmd = "gccxml --preprocess -dM "
    if fname:
        cmd += fname
    i, o = os.popen4(cmd)
    i.close()
    result = {}
    for line in o:
        if not line.startswith("#define "):
            # Is this an error, should we print it?
            continue
        line = line[len("#define "):].strip()
        items = line.split(None, 1)
        if len(items) < 2:
            log.write("empty definition: #define %s\n" % items[0])
            continue

        name, value = items
        if "(" in name: # we want only macros without parameters
            log.write("has params: #define %s %s\n" % (name, value))
            continue

        if value in C_KEYWORDS:
            log.write("rhs is keyword: #define %s %s\n" % (name, value))
            continue

        if name in EXCLUDED:
            log.write("excluded: #define %s %s\n" % (name, value))
            continue

        # This is probably not correct: What when one of these characters is in a string literal?
        if value and value[0] in r"=/{};" \
           or value and value[-1] in r"=/{};":
            log.write("won't work: #define %s %s\n" % (name, value))
            continue

        if wordpat.match(name) and wordpat.match(value):
            # XXX aliases should be handled later, when (and if!) the rhs is known
            log.write("alias: #define %s %s\n" % (name, value))
            continue

        result[name] = value
    return result

def gccxml_get_defines(fname):
    """Find the preprocessor definitions in file <fname>.

    Do not return symbols defined as keywords, macros with parameters,
    or symbols defined by the C compiler itself."""
    # find predefined symbols
    predefs = _gccxml_get_defines(None)
    # find defined symbols in this file
    defs = _gccxml_get_defines(fname)
    skipped = 0
    for name in predefs:
        log.write("predefined compiler symbol: #define %s %s\n" % (name, defs[name]))
        del defs[name]
        skipped += 1
    print "skipped %d predefined symbols" % skipped
    return defs


def c_type_name(tp):
    """Return the C type name for this type.
    """
    if isinstance(tp, typedesc.FundamentalType):
        return tp.name
    elif isinstance(tp, typedesc.PointerType):
        return "%s *" % c_type_name(tp.typ)
    elif isinstance(tp, typedesc.CvQualifiedType):
        return c_type_name(tp.typ)
    elif isinstance(tp, typedesc.Typedef):
        return c_type_name(tp.typ)
    elif isinstance(tp, typedesc.Structure):
        return tp.name
    raise TypeError, type(tp).__name__

################################################################
def create_file():
    ofi = open("glut.cpp", "w")
##    ofi.write('#include <gl/glut.h>\n')
#    ofi.write("#define WIN32_LEAN_AND_MEAN\n")
    ofi.write('#include <windows.h>\n')
    return ofi
    
################################################################
# parse a C header file, and dump the preprocessor symbols
create_file()

# find the preprocessor defined symbols
print "... finding preprocessor symbol names"
defs = gccxml_get_defines("glut.cpp")
print "%d '#define' symbols found" % len(defs)

names = set(defs.keys())
values = set(defs.values())
print "%d unique names, %d unique values" % (len(names), len(values))
print "removed %d aliases" % (len(names & values))
for n in (names & values):
    del defs[n]

################################################################
# parse the standard output
print "... processing with gccxml"
os.system("gccxml glut.cpp -fxml=glut.xml")

print "... parsing gccxml output:",
items = parse("glut.xml")
print "%d type descriptions found" % len(items)

types = {}
for i in items:
    name = getattr(i, "name", None)
    if name:
        types[name] = i

##interesting = (typedesc.Function,)
##interesting = (typedesc.EnumValue,)
interesting = (typedesc.FundamentalType, typedesc.Function, typedesc.FunctionType,
               typedesc.Typedef)

# XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX here continue to work...

# filter the symbols ...
newdefs = {}
skipped = 0
known = set()
for name, value in defs.iteritems():
    if value in types:
        # Ah, we know the *type* and the *value* of this item already
        skipped += 1
##        print "SKIPPED", type(types[value]).__name__, name, value
        known.add(name)
        pass
    else:
        newdefs[name] = value
print "skipped %d symbols, type and value are known from XML" % skipped
print "Remaining %s items" % len(newdefs)

defs = newdefs

for name in defs.keys():
    if name.startswith("DECLSPEC") or defs[name].startswith("DECLSPEC"):
        del defs[name]
print "Remaining %s items after removing DECLSPEC..." % len(defs)

################################################################
# invoke some C++ magic, which will create a lot of functions.
# The function name can later be used to retrieve the symbol name again,
# and the function's return type is the symbols's type.
ofi = create_file()
MAGIC = """
#define DECLARE(sym) \
template <typename T> T symbol_##sym(T, T val = sym) {}

#define DEFINE(sym) \
symbol_##sym(sym, sym)
"""
ofi.write(MAGIC)
for name in defs:
    ofi.write("// #define %s %s\n" % (name, defs[name]))
    ofi.write("DECLARE(%s)\n" % name);
ofi.write("int main() {\n")
for name in defs:
    ofi.write("  DEFINE(%s);\n" % name);
ofi.write("}\n")
ofi.close()

print "... finding preprocessor symbol types"
# compile the file
os.system("gccxml glut.cpp -fxml=glut.xml")

# parse the result
items = parse("glut.xml")

# create a new C++ file which will later allow to retrieve the name,
# the type and the value of the preprocessor definitions from the
# gccxml created output.
codelines = []
for i in items:
    if i.name and i.name.startswith("symbol_"):
        symname = i.name[len("symbol_"):]
        try:
            symtype = c_type_name(i.returns)
        except TypeError, detail:
            print "// skipped #define %s %s" % (symname, defs[symname]), detail
            # HWNDNOTOPMOST: ((HWND) -2), HWND is a structure
            continue
        codelines.append("const %s cpp_sym_%s = %s;" % (symtype, symname, symname))

print "created %d definitions" % len(codelines)

ofi = create_file()
for c in codelines:
    ofi.write("%s\n" % c)
ofi.close()

################################################################
# parse the resulting file with gccxml, to create the xml that
# will be used to generate Python code
print "... finding preprocessor symbol values"
os.system("gccxml glut.cpp -fxml=glut.xml")
