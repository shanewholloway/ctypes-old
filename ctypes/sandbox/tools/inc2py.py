# A script which parses C header files, translates #define statements
# into Python code.
#
# Requires that gccxml from http://www.gccxml.org/ is installed and on
# the PATH.
#
# Inspired and partly derived from Python's tools/scripts/h2py.py, but
# the include files are passed to a real C preprocessor first, which
# then dumps out the #defines to be translated and executed by this script.
#
# This script generates:
# - valid Python code, which can be written to a file and imported
#   as Python module later,
# - a dictionary containing the results of evaluating all the generated
#   Python expressions


# Here are some comments from the h2py script:
#
# Read #define's and translate to Python code.
# Handle #define macros with one argument.
# Anything that isn't recognized or doesn't translate into valid
# Python is ignored.

# By passing one or more options of the form "-i regular_expression"
# you can specify additional strings to be ignored.  This is useful
# e.g. to ignore casts to u_long: simply specify "-i '(u_long)'".

# XXX To do:
# - turn C Boolean operators "&& || !" into Python "and or not"
# - what to do about macros with multiple parameters?

import sys, re, os, tempfile
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# regular expressions to find #define's
p_define = re.compile('^#define[\t ]+([a-zA-Z0-9_]+)[\t ]+')
p_macro = re.compile(
  '^#define[\t ]+'
  '([a-zA-Z0-9_]+)\(([_a-zA-Z][_a-zA-Z0-9]*)\)[\t ]+')

# patterns to replace by a single blank (platform specific)
if sys.platform == "win32":
    # ignore type casts.  Sounds strange, but works.
    ignores = r"""
    \(\s*HRESULT\s*\)
    \(\s*BYTE\s*\)
    \(\s*WCHAR\s*\)
    \(\s*WORD\s*\)
    \(\s*USHORT\s*\)
    \(\s*SHORT\s*\)
    \(\s*DWORD\s*\)
    \(\s*UINT\s*\)
    \(\s*INT\s*\)
    \(\s*ULONG\s*\)
    \(\s*LONG\s*\)
    \(\s*BYTE\s*\)
    \(\s*LPSTR\s*\)
    \(\s*LPTSTR\s*\)
    \(\s*LPWSTR\s*\)
    \(\s*HKEY\s*\)
    \(\s*MCIDEVICEID\s*\)
    \(\s*HANDLE\s*\)
    \(\s*HWND\s*\)
    \(\s*HCURSOR\s*\)
    \(\s*HICON\s*\)
    \(\s*HDDEDATA\s*\)
    \(\s*int\s*\)
    \(\s*u_long\s*\)
    \(\s*unsigned\s*long\s*\)
    """
else:
    ignores = []

ignores = map(re.compile, ignores.strip().splitlines())

# a sequence of pattern / replacement pairs for macro bodies,
# passed to re.sub
replaces = [
    # Remove the U suffix from decimal constants
    (re.compile(r"(\d+)U"), r"\1"),
    # Remove the U suffix from hex constants
    (re.compile(r"(0[xX][0-9a-fA-F]+)U"), r"\1")
    ]

class ParserError(Exception):
    pass

# pass one or more include files to the preprocessor, and return a
# sequence of text lines containing the #define's that the
# preprocessor dumps out.
def get_cpp_symbols(*fnames):
    # write a temporary C file
    handle, c_file = tempfile.mkstemp(suffix=".c", text=True)
    for fname in fnames:
        os.write(handle, "#include <%s>\n" % fname)
    os.close(handle)

    try:
        # We don't want the predefined symbols. So we get them and
        # remove them later.
        i, o = os.popen4(r"gccxml.exe --preprocess -dM")
        i.close()
        builtin_syms = o.readlines()
        retval = o.close()
        if retval:
            raise ParserError, "gccxml returned error %s" % retval

        result = []
        print (r"# gccxml.exe %s --preprocess -dM" % c_file)
        i, o = os.popen4(r"gccxml.exe %s --preprocess -dM" % c_file)
        i.close()
        for line in o.readlines():
            if not line in builtin_syms:
                result.append(line)
        retval = o.close()
        if retval:
            raise ParserError, "gccxml returned error %s" % retval
        return result
    finally:
        os.remove(c_file)


class IncludeParser(object):

    def __init__(self, env=None):
        if env is None:
            self.env = {}
        else:
            self.env = env
        self.statements = []

    # ripped from h2py
    def pytify(self, body):
        # replace ignored patterns by spaces
        for p in ignores:
            body = p.sub(' ', body)
        for pat, repl in replaces:
            body = pat.sub(repl, body)
        return body

    def parse(self, *files):
        self._parse(*files)
        del self.env["__builtins__"]

    def _parse(self, *files):
        self.files = files
        lines = get_cpp_symbols(*files)

        total = 0
        for i in range(10):
            processed = self.create_pycode(lines)
            total += processed
            print "processed %d (%d) defs in pass %d, %d defs remain" % \
                  (processed, total, i, len(lines))
            if not processed:
                return

    def create_pycode(self, lines):
        processed = [] # line numbers of processed lines
        for lineno, line in enumerate(lines):
            match = p_define.match(line)
            if match:
                name = match.group(1)
                if name in self.env:
                    continue
                body = line[match.end():]
                body = self.pytify(body)
                stmt = '%s = %s\n' % (name, body.strip())
                try:
                    exec stmt in self.env
                except:
                    pass
                else:
                    self.statements.append(stmt)
                    processed.append(lineno)
                continue

            match = p_macro.match(line)
            if match:
                macro, arg = match.group(1, 2)
                if macro in self.env:
                    continue
                body = line[match.end():]
                body = self.pytify(body)
                stmt = 'def %s(%s): return %s\n' % (macro, arg, body)
                try:
                    exec stmt in self.env
                except:
                    pass
                else:
                    self.statements.append(stmt)
                    processed.append(lineno)
                continue

            # no pattern matches, cannot process this line
            processed.append(lineno)

        processed.reverse()
        for i in processed:
            del lines[i]
        return len(processed)

# script start
if __name__ == "__main__":
    import time
    import types
    os.environ["GCCXML_COMPILER"] = "msvc71"
    
    parser = IncludeParser()
    start = time.clock()
    parser.parse("windows.h", "sqlX.h")
    print "%.2f seconds" % (time.clock() - start)
    
    n = 0
    ofi = open("symbols.py", "w")
    names = parser.env.keys()
    names.sort() # it's nicer
    for name in names:
        value = parser.env[name]
        if not type(value) is types.FunctionType:
            ofi.write("%s = %r\n" % (name, value))
            n += 1
    print "Dumped %d symbols" % n
