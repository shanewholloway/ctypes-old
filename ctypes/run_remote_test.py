# Todo: handle import error the same way as test errors.
import os, sys, unittest

class TestFile(object):
    def __init__(self, path):
        self.path = path
    def shortDescription(self):
        return self.path
    failureException = AssertionError

if __name__ == "__main__":
    pathname = sys.argv[1]
    dirname, filename = os.path.split(pathname)
    basename, ext = os.path.splitext(filename)

    del sys.argv[1]
    sys.path.append(dirname)


    if 0:
        stream = open("test.output", "w")
        runner = unittest.TextTestRunner(stream, verbosity=2)
    else:
        # Strange, this path crashes with Python 2.3.4, release build,
        # on Windows XP, unless we write to stdout. An empty string!
        # Doesn't crash with Python 2.4.
        sys.stdout.write("")
        runner = unittest.TextTestRunner(open("test.output", "w"), verbosity=2)
    try:
        unittest.main(module=__import__(basename), testRunner=runner)
    except SystemExit:
        pass
    except:
        result = runner._makeResult()
        err = sys.exc_info()
        result.addError(TestFile(pathname), err)
        result.printErrors()
        result.stream.write("%s (could not import) ... ERROR\n" % pathname)
