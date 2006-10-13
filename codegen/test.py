import sys, os

os.system(sys.executable + " -m h2xml -I. test.h -o test.xml")
os.system(sys.executable + " -m xml2py test.xml -o _test.py")

g = {}
l = {}
execfile("_test.py", g)
for name in "i ui i64 ui64".split():
    try:
        val = g[name]
    except KeyError:
        continue
    print name, g[name], hex(g[name])
