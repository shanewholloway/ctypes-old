import os, sys, re

pat = re.compile("^#define ([a-zA-Z0-9_]+) .+")

PROG = r'''\
#include "dump.h"
#include "includes.h"

int main()
{
%s
    return 0;
}
'''

cmd = "cl /nologo /Zi -D _WIN32_WINNT=0x500 temp.cpp"

try:
    os.remove("constants.py")
except OSError, details:
    if details.errno != 2:
        raise

# fakes - correspond to code in dump.h
PY_HEADER = """\
def LPCSTR(x):
    return x
def LPSTR(x):
    return x
def GUID(x):
    return x

"""

open("constants.py", "w").write(PY_HEADER)

try:
    data = open("skipped.txt", "r").read()
except IOError, details:
    if details.errno != 2:
        raise
    data = ""
        
skipped = data.splitlines()

syms = []
for line in open(sys.argv[1]):
    match = pat.match(line)
    if match:
        symbol = match.group(1)
        if symbol in skipped:
            continue
        syms.append(symbol)

syms.sort()

CHUNKSIZE = len(syms)

done = 0

while syms:
    skipped = []
    while syms:
        now = syms[:CHUNKSIZE]
        syms = syms[CHUNKSIZE:]
        text = "\n".join(["    DUMP(%s);" % s for s in now])
        open("temp.cpp", "w").write(PROG % text)
        print "\t[%s .. %s]... " % (now[0], now[-1]),
        failed = os.system(cmd)
        if failed:
            print "failed"
        if not failed:
            os.system("temp.exe >> constants.py")
            print "%d ok" % len(now)
            done += len(now)
            print "%d done, %d remain" % (done, len(syms + skipped))
        else:
            skipped.extend(now)
    if CHUNKSIZE > 512:
        CHUNKSIZE = 512
    else:
        CHUNKSIZE /= 8
    if CHUNKSIZE == 0:
        print "FAILED on %d symbols" % (len(syms) + len(skipped))
        errfile = open("skipped.txt", "a+")
        for n in syms + skipped:
            errfile.write("%s\n" % n)
        sys.exit()
    print "try CHUNKSIZE", CHUNKSIZE
    syms = skipped
