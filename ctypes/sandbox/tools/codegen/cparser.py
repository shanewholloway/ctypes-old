import sys, os, re, tempfile
from cparser_config import C_KEYWORDS, EXCLUDED, EXCLUDED_RE
import gccxmlparser, typedesc

if sys.platform == "win32":

    def _locate_gccxml():
        import _winreg
        for subkey in (r"Software\gccxml", r"Software\Kitware\GCC_XML"):
            for root in (_winreg.HKEY_CURRENT_USER, _winreg.HKEY_LOCAL_MACHINE):
                try:
                    hkey = _winreg.OpenKey(root, subkey, 0, _winreg.KEY_READ)
                except WindowsError, detail:
                    if detail.errno != 2:
                        raise
                else:
                    return _winreg.QueryValueEx(hkey, "loc")[0] + r"\bin"

    loc = _locate_gccxml()
    if loc:
        os.environ["PATH"] = loc

class CompilerError(Exception):
    pass

class IncludeParser(object):

    def create_source_file(self, lines, ext=".cpp"):
        "Create a temporary file, write lines to it, and return the filename"
        fd, fname = tempfile.mkstemp(ext, text=True)
        stream = os.fdopen(fd, "w")
        if lines:
            for line in lines:
                stream.write("%s\n" % line)
        stream.close()
        return fname

    def compile_and_dump(self, lines=None):
        """Create a temporary source file, dump preprocessor
        definitions, and remove the source file again."""
        fname = self.create_source_file(lines)
        try:
            args = ["gccxml", "--preprocess", "-dM", fname]
            if self.options.flags:
                args.append(self.options.flags)
            i, o = os.popen4(" ".join(args))
            i.close()
            data = o.read()
        finally:
            os.remove(fname)
        return [line[len("#define "):]
                for line in data.splitlines()
                if line.startswith("#define ")]

    def create_xml(self, lines, xmlfile):
        """Create a temporary source file, 'compile' with gccxml to an
        xmlfile, and remove the source file again."""
        fname = self.create_source_file(lines)
        args = ["gccxml", fname, "-fxml=%s" % xmlfile]
        if self.options.flags:
            args.append(self.options.flags)
        try:
            retcode = os.system(" ".join(args))
            if retcode:
                raise CompilerError, "gccxml returned %s" % retcode
        finally:
            os.remove(fname)

    def get_defines(self, include_file):
        """'Compile' an include file with gccxml, and return a
        dictionary of preprocessor definitions.  Empty and compiler
        internal definitions are not included."""
        # compiler internal definitions
        lines = self.compile_and_dump()
        predefined = [line.split(None, 1)[0]
                      for line in lines]
        # all definitions
        lines = self.compile_and_dump(['#include "%s"' % include_file])
        defined = [line.split(None, 1)
                   for line in lines]
        # remove empty and compiler internal definitions
        defined = [pair for pair in defined
                   if len(pair) == 2 and pair[0] not in predefined]

        return dict(defined)

    wordpat = re.compile("^[a-zA-Z_][a-zA-Z0-9_]*$")
    def is_excluded(self, name, value):

        INVALID_CHARS = "=/{}&;"
        if "(" in name:
            return "macro with parameters"
        if value in C_KEYWORDS:
            return "value is keyword"
        if name in EXCLUDED:
            return "excluded"
        for pat in EXCLUDED_RE:
            if pat.match(name):
                return "excluded (regex)"
        if value[0] in INVALID_CHARS or value[-1] in INVALID_CHARS:
            return "cannot be a value"
        if self.wordpat.match(name) and self.wordpat.match(value):
            # aliases are handled later, when (and if!) the rhs is known
            return "IS_ALIAS"
        return False

    def filter_definitions(self, defines):
        "Return a dict of aliases, and another dict of constants and literals"
        result = {}
        aliases = {}
        for name, value in defines.iteritems():
            why = self.is_excluded(name, value)
            if why == "IS_ALIAS":
                aliases[name] = value
            if not why:
                result[name] = value
        return aliases, result

    ################################################################

    def find_types(self, include_file, defines):
        source = []
        source.append('#include "%s"' % include_file)
        source.append("#define DECLARE(sym) template <typename T> T symbol_##sym(T) {}")
        source.append("#define DEFINE(sym) symbol_##sym(sym)")
        for name in defines:
            # create a function template for each value
            source.append("DECLARE(%s)" % name)
        source.append("int main() {")
        for name in defines:
            # instantiate a function template.
            # The return type of the function is the symbol's type.
            source.append("  DEFINE(%s);" % name)
        source.append("}")

        fd, fname = tempfile.mkstemp(".xml")
        os.close(fd)
        self.create_xml(source, fname)
        try:
            items = gccxmlparser.parse(fname)
        finally:
            # make sure the temporary file is removed after using it
            os.remove(fname)

        types = {}
        for i in items:
            name = getattr(i, "name", None)
            if name and name.startswith("symbol_"):
                name = name[len("symbol_"):]
                typ = i.returns
                try:
                    typ = self.c_type_name(i.returns)
                except TypeError, detail:
                    # XXX Warning?
                    print >> sys.stderr,  "skipped #define %s %s" % (name, defines[name]), detail
                else:
                    types[name] = typ
        return types

    def create_final_xml(self, include_file, types):
        source = []
        source.append('#include "%s"' % include_file)
        for name, value in types.iteritems():
            source.append("const %s cpp_sym_%s = %s;" % (types[name], name, name))
        fname = self.options.xmlfile
        self.create_xml(source, fname)

    def c_type_name(self, tp):
        "Return the C type name for this type."
        if isinstance(tp, typedesc.FundamentalType):
            return tp.name
        elif isinstance(tp, typedesc.PointerType):
            return "%s *" % self.c_type_name(tp.typ)
        elif isinstance(tp, typedesc.CvQualifiedType):
            return self.c_type_name(tp.typ)
        elif isinstance(tp, typedesc.Typedef):
            return self.c_type_name(tp.typ)
        elif isinstance(tp, typedesc.Structure):
            return tp.name
        raise TypeError, type(tp).__name__

    ################################################################

    def parse(self, include_file, options):
        """Main method.

        The options object must have these attribuites:
          verbose - integer
          flags - string
        """
        self.options = options

        if options.verbose:
            print >> sys.stderr, "finding definitions ..."
        defines = self.get_defines(include_file)
        if options.verbose:
            print >> sys.stderr, "%d found" % len(defines)

            print >> sys.stderr, "filtering definitions ..."
        aliases, defines = self.filter_definitions(defines)
        if options.verbose:
            print >> sys.stderr, "%d values, %d aliases" % (len(defines), len(aliases))

        if options.verbose:
            print >> sys.stderr, "finding definitions types ..."
            # invoke C++ template magic
        types = self.find_types(include_file, defines)
        if options.verbose:
            print >> sys.stderr, "found %d types ..." % len(types)

        if options.verbose:
            print >> sys.stderr, "creating xml output file ..."
        self.create_final_xml(include_file, types)
        # Should we now insert the aliases into the xml, again?
        
##if __name__ == "__main__":
##    class options(object):
##        pass
##    options = options()

##    options.verbose = 1
##    options.flags = "-D WIN32_LEAN_AND_MEAN -D NO_STRICT"

##    p = IncludeParser()
##    options.xmlfile = "windows.xml"
##    p.parse("windows.h", options)
