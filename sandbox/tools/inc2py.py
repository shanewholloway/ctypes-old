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
"""
Usage: inc2py [options] files...

This program parses C include files and converts #define statements
into Python code.  It requires that the GCCXML C++ parser from
http://www.gccxml.org/ is installed and on the PATH.

Command line flags:

   -c <value>, --compiler <value>
      Specifies the compiler that GCCXML should emulate.  For Windows,
      typically use msvc6 or msvc71.

   -D <symbol>
   -D <symbol=value>
   -U <symbol>
   -I <directory>
      These flags are passed to GCCXML.

   -o <filename>
      Write the parsing results to <filename>.  Using '-' as filename
      will write the results to standard output.

   -r
      Create the output file in raw format - default is non-raw.

      In non-raw format, only constant values are written to the
      output file, sorted by names.

      In raw format, the names are not sorted, C macros are included
      as Python functions, and the last section of the file will
      contain the #define directives that could not be parsed.

   -v
      Increases the verbosity.  Verbosity 1 prints out what the
      program is doing, verbosity 2 additionally prints lines it could
      not parse.

   -h
      Display help, and quit.

   For a start (on windows), try this:

      inc2py.py -D _WIN32_WINNT=0x500 -c msvc71 -o windows.py windows.h
"""

import sys, re, os, tempfile
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# regular expressions to find #define's
p_define = re.compile('^#define[\t ]+([a-zA-Z0-9_]+)[\t ]+')
p_macro = re.compile(
  '^#define[\t ]+'
  '([a-zA-Z0-9_]+)\(([_a-zA-Z][_a-zA-Z0-9]*)\)[\t ]+')

# patterns to replace by a single blank (platform specific)
# ignore type casts.  Sounds strange, but works.

if sys.platform == "win32":
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
    \(\s*HKEY\s*\)
    \(\s*HCURSOR\s*\)
    \(\s*HBITMAP\s*\)
    \(\s*HICON\s*\)
    \(\s*HDDEDATA\s*\)
    \(\s*NTSTATUS\s*\)
    \(\s*int\s*\)
    \(\s*u_long\s*\)
    \(\s*ULONG_PTR\s*\)
    \(\s*unsigned\s*long\s*\)
    """
else:
    ignores = []

ignores = [re.compile(p.strip()) for p in ignores.strip().splitlines()]

# a sequence of pattern / replacement pairs for macro bodies,
# passed to re.sub
replaces = [
    # Remove the U suffix from decimal constants
    (re.compile(r"(\d+)U"), r"\1"),
    # Remove the U suffix from hex constants
    (re.compile(r"(0[xX][0-9a-fA-F]+)U"), r"\1"),
    # Replace L"spam" with u"spam"
    (re.compile(r'[lL]("[^"]*")'), r"u\1")
    ]

class ParserError(Exception):
    pass

# pass one or more include files to the preprocessor, and return a
# sequence of text lines containing the #define's that the
# preprocessor dumps out.
def get_cpp_symbols(options, verbose, *fnames):
    # options is a sequence of command line options for GCCXML
    # fnames is the sequence of include files
    #

    compiler = ""
    for o in options:
        if o.startswith("--gccxml-compiler"):
            compiler = o
    options = " ".join(options)

    # write a temporary C file
    handle, c_file = tempfile.mkstemp(suffix=".c", text=True)
    for fname in fnames:
        os.write(handle, '#include <%s>\n' % fname)
    os.close(handle)

    def read_stderr(fd):
        import threading

        def get_errout(fd):
            errs = fd.read()
            if errs:
                sys.stderr.write(errs)
            retval = fd.close()
            if retval:
                raise ParserError, "gccxml returned error %s" % retval

        thread = threading.Thread(target=get_errout, args=(fd,))
        thread.start()
        return thread

    try:
        # We don't want the predefined symbols. So we get them and
        # remove them later.
        if verbose:
            print >> sys.stderr, r"run gccxml.exe %s --preprocess -dM" % compiler
        i, o, e = os.popen3(r"gccxml.exe %s --preprocess -dM" % compiler)
        t = read_stderr(e)
        i.close()
        builtin_syms = o.readlines()
        retval = o.close()
        if retval:
            raise ParserError, "gccxml returned error %s" % retval
        t.join()

        result = []
        if verbose:
            print >> sys.stderr, r"run gccxml.exe %s %s --preprocess -dM" % (options, c_file)
        i, o, e = os.popen3(r"gccxml.exe %s %s --preprocess -dM" % (options, c_file))
        t = read_stderr(e)
        i.close()
        for line in o.readlines():
            if not line in builtin_syms:
                result.append(line)
        retval = o.close()
        t.join()
        if retval:
            raise ParserError, "gccxml returned error %s" % retval
        return result
    finally:
        if verbose:
            print >> sys.stderr, "Deleting temporary file %s" % c_file
        os.remove(c_file)

################################################################

class IncludeParser(object):

    def __init__(self, cpp_options=(), verbose=0, env=None):
        if env is None:
            self._env = {}
        else:
            self._env = env
        self._statements = []
        self._errlines = []
        self._cpp_options = cpp_options
        self._verbose = verbose

    # ripped from h2py
    def pytify(self, body):
        # replace ignored patterns by spaces
        for p in ignores:
            body = p.sub(' ', body)
        for pat, repl in replaces:
            body = pat.sub(repl, body)
        return body

    def parse(self, *files):
        remaining = self._parse(*files)
        self._env.pop("__builtins__", None)
        # self._errlines are lines we do not know how to handle, and
        # self.lines are the remaining lines where we know how to
        # handle them but fail.
        self._errlines = self._errlines + remaining

    def _parse(self, *files):
        self.files = files
        lines = get_cpp_symbols(self._cpp_options, self._verbose, *files)

        if self._verbose:
            print >> sys.stderr, "Start parsing..."
        total = 0
        for i in range(10):
            processed = self.parse_lines(lines)
            total += processed
            if self._verbose:
                print >> sys.stderr, "processed %d (%d) defs in pass %d, %d defs remain" % \
                      (processed, total, i, len(lines))
            if not processed:
                break
        if self._verbose > 1:
            for line in lines:
                print >> sys.stderr, "Skipped '%s'" % line.rstrip("\n")
        if self._verbose:
            print >> sys.stderr, "Parsing done."

        return lines

    def create_statement(self, line):
        match = p_define.match(line)
        if match:
            name = match.group(1)
            body = line[match.end():]
            body = self.pytify(body)
            return '%s = %s\n' % (name, body.strip())

        match = p_macro.match(line)
        if match:
            macro, arg = match.group(1, 2)
            body = line[match.end():]
            body = self.pytify(body)
            return 'def %s(%s): return %s\n' % (macro, arg, body)
        return None

    def parse_lines(self, lines):
        processed = [] # line numbers of processed lines
        for lineno, line in enumerate(lines):
            stmt = self.create_statement(line)
            if stmt is None: # cannot process this line
                self._errlines.append(line)
                processed.append(lineno)
            else:
                try:
                    exec stmt in self._env
                except Exception:
                    pass
                else:
                    self._statements.append(stmt)
                    processed.append(lineno)

        processed.reverse()
        for i in processed:
            del lines[i]
        return len(processed)

    def get_symbols(self):
        # return a dictionary containing the symbols collected
        return self._env.copy()

    def get_statements(self):
        # return a sequence of Python statements generated from the #defines
        return self._statements[:]

    def get_errlines(self):
        # return a sequence of #define lines which could not be processed
        return self._errlines[:]

    def write_symbols(self, fname, raw):
        import types
        if fname == "-":
            ofi = sys.stdout
        else:
            ofi = open(fname, "w")
        if raw:
            for s in self._statements:
                ofi.write(s)
            ofi.write("\n\n##### skipped lines #####\n\n")
            for s in self._errlines:
                ofi.write(s)
        else:
            symbols = self.get_symbols()
            names = symbols.keys()
            names.sort() # it's nicer
            for name in names:
                value = symbols[name]
                if not type(value) is types.FunctionType:
                    ofi.write("%s = %r\n" % (name, value))
        
################################################################

def main(args=sys.argv[1:]):
    import getopt

    gccxml_options = []
    verbose = 0
    py_file = None
    raw = 0
    try:
        opts, files = getopt.getopt(args, "hrvc:D:U:I:o:", ["compiler="])
    except (getopt.GetoptError, ValueError), details:
        print "Error:", details
        print >> sys.stderr, __doc__
        return 1
    for o, a in opts:
        if o in ("-c", "--compiler"):
            gccxml_options.append("--gccxml-compiler %s" % a)
        elif o in ("-D", "-U", "-I"):
            gccxml_options.append("%s %s" % (o, a))
        elif o == "-o":
            py_file = a
        elif o == "-v":
            verbose += 1
        elif o == "-r":
            raw = 1
        elif o == "-h":
            print >> sys.stderr, __doc__
            return 0

    if not files:
        print "Error: no files to process"
        print >> sys.stderr, __doc__
        return 1
    
    parser = IncludeParser(gccxml_options, verbose=verbose)
    parser.parse(*files)
    if py_file:
        parser.write_symbols(py_file, raw)
    return 0

if __name__ == "__main__":
    sys.exit(main())
