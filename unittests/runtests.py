"""Usage: runtests.py [-q] [-v] [mask]

Run all tests found in this directory, and print a summary of the results.
Command line flags:
  -v     verbose mode: print the test currently executed
  -q     quiet mode: don't prnt anything while the tests are running
  mask   mask to select filenames containing testcases, wildcards allowed
"""
import glob, os, sys, unittest, getopt

def get_suite(mask):
    if not mask.endswith(".py"):
        mask += ".py"
    test_suites = []
    for fname in glob.glob(mask):
        try:
            mod = __import__(os.path.splitext(fname)[0])
        except Exception, detail:
            print "Warning: could not import %s: %s" % (fname, detail)
            continue
        for name in dir(mod):
            if name.startswith("_"):
                continue
            o = getattr(mod, name)
            if type(o) is type(unittest.TestCase) and issubclass(o, unittest.TestCase):
                test_suites.append(unittest.makeSuite(o))
    return unittest.TestSuite(test_suites)

def usage():
    print __doc__
    return 1

def main():
    verbosity = 1
    mask = "test_*.py"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "qv")
    except getopt.error:
        return usage()
    for flag, value in opts:
        if flag == "-q":
            verbosity -= 1
        elif flag == "-v":
            verbosity += 1
    if args:
        mask = args[0]
    suite = get_suite(mask)
    runner = unittest.TextTestRunner(verbosity=verbosity)
    return bool(runner.run(suite).errors)


if __name__ == "__main__":
    sys.exit(main())
