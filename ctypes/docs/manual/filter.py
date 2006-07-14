# Remove rest modifiers from the input files, write to stdout
import sys

TOKENS = """: funcdesc
: excdesc
: vardesc
: classdesc
: methoddesc
: memberdesc
: funcdescni
: classdesc*""".splitlines()

for ifi in sys.argv[1:]:
    for line in open(ifi, "r"):
        for token in TOKENS:
            line = line.rstrip()
            if line.endswith(token):
                print line[:-len(token)]
                break
        else:
            print line
