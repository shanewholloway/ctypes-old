import sys

TOKENS = """: funcdesc
: excdesc
: vardesc
: classdesc
: methoddesc
: memberdesc
: classdesc*""".splitlines()

for line in open(sys.argv[1], "r"):
    for token in TOKENS:
        line = line.rstrip()
        if line.endswith(token):
            print line[:-len(token)]
            break
    else:
        print line
