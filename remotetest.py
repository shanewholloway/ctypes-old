import unittest
import os, sys
import cPickle

class TestFile(object):
    def __init__(self, path):
        self.path = path
    def shortDescription(self):
        return self.path
    failureException = AssertionError

class RemoteTestRunner(unittest.TextTestRunner):
    # Differences from unittest.TextTestRunner:
    # - _makeResult() takes an optional parameter used to initialize the TestResult
    # - run() accepts a TestResult instance
    # - run() only runs the tests, does no reporting
    # - separate report() method
    # - run_file method
    def _makeResult(self, options=None):
        result = unittest.TextTestRunner._makeResult(self)
        if options is not None:
            result.__dict__.update(options)
        return result

    def run_file(self, fname, result=None):
        dirname, filename = os.path.split(fname)
        modname = os.path.splitext(filename)[0]

        if dirname not in sys.path:
            sys.path.insert(0, dirname)
        try:
            mod = __import__(modname, globals(), locals(), [""])
        except:
            if self.verbosity == 2:
                self.stream.write("%s ... could not import " % fname)
            result.addError(TestFile(fname), sys.exc_info())
            return result

        test_classes = []
        for name in dir(mod):
            if name.startswith("_"):
                continue
            o = getattr(mod, name)
            if type(o) is type(unittest.TestCase) and issubclass(o, unittest.TestCase):
                test_classes.append(o)

        for item in test_classes:
            result = self.run(unittest.makeSuite(item), result)
        return result

    def run(self, test, result=None):
        "Run the given test case or test suite."
        if result is None:
            result = self._makeResult()
        test(result)
        return result

    def report(self, result, duration=None):
        "Report the test results."
        result.printErrors()
        self.stream.writeln(result.separator2)
        run = result.testsRun
        if duration is not None:
            self.stream.writeln("Ran %d tests in %.3f s" % (run, duration))
        else:
            self.stream.writeln("Ran %d tests" % run)
        self.stream.writeln()
        if not result.wasSuccessful():
            self.stream.write("FAILED (")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                self.stream.write("failures=%d" % failed)
            if errored:
                if failed: self.stream.write(", ")
                self.stream.write("errors=%d" % errored)
            self.stream.writeln(")")
        else:
            self.stream.writeln("OK")

################################################################

def server(verbose, args, pickle_name):
    runner = RemoteTestRunner(sys.stderr, 1, verbosity=verbose)

    for a in args:
        p = os.path.dirname(a)
        if p not in sys.path:
            sys.path.insert(0, p)
    d = cPickle.load(open(pickle_name, "r"))

    result = runner._makeResult(d)
    for a in args:
        result = runner.run_file(a, result)
    sys.path.insert(0, os.path.dirname(a))
    options = {}
    for name in "errors failures testsRun".split():
        options[name] = getattr(result, name)

    cPickle.dump(options, open(pickle_name, "w"))

################################################################

def client(verbose, args):
    import glob, time, tempfile
    L = []
    for a in args:
        L.extend(glob.glob(a))
    args = L

    runner = RemoteTestRunner(sys.stderr, 1, verbosity=verbose)
    d = {"errors": [], "failures": [], "testsRun": 0}

    starttime = time.time()
    for a in args:
        p = os.path.dirname(a)
        if p not in sys.path:
            sys.path.insert(0, p)
        cPickle.dump(d, open(".result.pck", "w"))
        if verbose == 2:
            os.system("%s remotetest.py -v -p %s %s" % (sys.executable, ".result.pck", a))
        elif verbose == 1:
            os.system("%s remotetest.py -p %s %s" % (sys.executable, ".result.pck", a))
        else:
            os.system("%s remotetest.py -q -p %s %s" % (sys.executable, ".result.pck", a))
        d = cPickle.load(open(".result.pck", "r"))
        result = runner._makeResult(d)
        os.unlink(".result.pck")
    runner.report(result, duration = time.time() - starttime)

################################################################

def main():
    import getopt

    verbose = 1
    pickle_name = None

    opts, args = getopt.getopt(sys.argv[1:], "qvp:")
    for o, a in opts:
        if o == "-q":
            verbose = 0
        elif o == "-v":
            verbose = 2
        elif o == "-p":
            pickle_name = a

    if pickle_name: # server mode
        server(verbose, args, pickle_name)
    else: # client mode: run tests in remote process
        client(verbose, args)

if __name__ == "__main__":
    main()
