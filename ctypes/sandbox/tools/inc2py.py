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
        i, o = os.popen4(r"gccxml.exe --preprocess -dM")
        i.close()
        ignores = o.readlines()

        result = []
        log = open("temp.log", "w")

        print (r"# gccxml.exe %s --preprocess -dM" % c_file)
        i, o = os.popen4(r"gccxml.exe %s --preprocess -dM" % c_file)
        i.close()
        for line in o.readlines():
            log.write(line)
            if not line in ignores:
                result.append(line)
        return result
    finally:
        os.remove(c_file)

##ignores = []

# ripped from h2py
def pytify(body):
    # replace ignored patterns by spaces
    for p in ignores:
        body = p.sub(' ', body)
    for pat, repl in replaces:
        body = pat.sub(repl, body)
    return body

def create_pycode(lines, env, stream, include_errors = False):
    errors = 0

    def try_stmt(stmt):
        try:
            exec stmt in env
        except:
            if include_errors and stream:
                stream.write("# %s" % stmt)
            return 1
        else:
            if stream:
                stream.write(stmt)
        return 0

    for line in lines:
        match = p_define.match(line)
        if match:
            name = match.group(1)
            if name in env:
                continue
            body = line[match.end():]
            body = pytify(body)
            stmt = '%s = %s\n' % (name, body.strip())
            errors += try_stmt(stmt)
            continue

        match = p_macro.match(line)
        if match:
            macro, arg = match.group(1, 2)
            if macro in env:
                continue
            body = line[match.end():]
            body = pytify(body)
            stmt = 'def %s(%s): return %s\n' % (macro, arg, body)
            errors += try_stmt(stmt)
            continue
        if include_errors and stream: # no pattern matches
            stream.write("# %s" % line)
            errors += 1
    return errors

# script start

os.environ["GCCXML_COMPILER"] = "msvc71"

lines = get_cpp_symbols("windows.h")#, "winsock.h")

ofi = sys.stdout

env = {}
e = 0
for i in range(10):
    errors = create_pycode(lines, env, ofi, None)
##    print "%d errors in pass %d" % (errors, i)
    if e == errors:
        create_pycode(lines, env, sys.stdout, True)
        print "# processed %d lines into %d definitions" % (len(lines), len(env))
        print "# %d errors remaining after %d passes" % (errors, i)
        break
    e = errors
