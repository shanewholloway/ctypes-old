#!/usr/bin/env python
import sys
import doctest
WINDOWS = doctest.register_optionflag("WINDOWS")
LINUX = doctest.register_optionflag("LINUX")
SKIP = doctest.register_optionflag("SKIP")

import ctypes
c_int_name = ctypes.c_int.__name__

base = doctest.DocTestRunner
class MyDocTestRunner(base):
    def run(self, test, compileflags=None, out=None, clear_globs=True):
        examples = test.examples[:]
        for ex in test.examples:
            if WINDOWS in ex.options and sys.platform != "win32":
                examples.remove(ex)
            elif LINUX in ex.options and not sys.platform.startswith("linux"):
                examples.remove(ex)
            elif SKIP in ex.options:
                examples.remove(ex)
            else:
##                print "REPLACE:"
##                print "\t", ex.want
##                print "\t", ex.want.replace("c_long", c_int_name)
                ex.want = ex.want.replace("c_long", c_int_name)
        test.examples = examples
        return base.run(self, test, compileflags, out, clear_globs)
doctest.DocTestRunner = MyDocTestRunner

if __name__ == "__main__":
    doctest.testfile("tutorial.txt",
                     optionflags=doctest.ELLIPSIS)
