# This is a test script, which uses both inc2py and parse_enums
# to create constant definitions from windows.h to wincon.py.
#
# The output shows that inc2py plus parse_enums create 12556 symbols
# not in win32con, and win32con has 71 symbols not in wincon.  A rough
# inspection shows that the 71 symbols are either not in the header
# files I have, or they are C macros converted to Python functions
# (sometimes correct, sometimes wrong) in win32con that the above
# toolchain does not (yet?) create.

# For the _WIN32_WINNT definition, see
# http://msdn.microsoft.com/library/en-us/winprog/winprog/using_the_windows_headers.asp

import os, sys
from xml.sax import parse
import inc2py
import parse_enums

files = ["windows.h", "richedit.h"]

gccxml_options = ["--gccxml-compiler msvc71",
                  "-D", "_WIN32_WINNT=0x500",
##                  "-D", "_WIN32_WINIE=0x600",
##                  "-D", "WINVER=0x500",
                  "-D", "OEMRESOURCE"]
verbose = 0

xml_file = parse_enums.run_gccxml(gccxml_options, verbose, *files)
handler = parse_enums.Enum_Handler()
parse(xml_file, handler)
os.remove(xml_file)

namespace = {}

for enum in handler.enums.values():
    for n, v in enum.values:
        namespace[n] = v

parser = inc2py.IncludeParser(gccxml_options, verbose=verbose, env=namespace)
parser.parse(*files)

parser.write_symbols("wincon.py", False)

################################################################

import wincon
import win32con

from sets import Set

a = Set(dir(wincon))
b = Set(dir(win32con))

##print len(a)
##print len(b)

print "wincon has %d symbols not in win32con" % len(a - b)
print "win32con has %d symbols not in wincon" % len(b - a)
##sys.exit()

common = list(a & b)
common.sort()

for name in common:
    v1 = getattr(win32con, name)
    v2 = getattr(wincon, name)
    if v1 != v2:
        print name, hex(v1), hex(v2)

sys.exit()

import pprint
missing = list(b - a)
missing.sort()
for name in missing:
    value = getattr(win32con, name)
    print name, value

