#!/usr/bin/env python
import sys
import doctest

# handle platform specific issues
WINDOWS = doctest.register_optionflag("WINDOWS")
LINUX = doctest.register_optionflag("LINUX")
OSX = doctest.register_optionflag("OSX")
SKIP = doctest.register_optionflag("SKIP")

# handle size specific issues
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
            elif OSX in ex.options and not sys.platform.startswith("darwin"):
                examples.remove(ex)
            elif SKIP in ex.options:
                examples.remove(ex)
            elif "printf(" in ex.source:
                # handle that doctest doesn't catch printf's output
                lines = ex.want.splitlines()
                try:
                    int(lines[-1])
                except ValueError:
                    pass
                else:
                    ex.want = "\n".join(lines[1:]) + "\n"
            else:
                ex.want = ex.want.replace("c_long", c_int_name)
        test.examples = examples
        return base.run(self, test, compileflags, out, clear_globs)
doctest.DocTestRunner = MyDocTestRunner

if __name__ == "__main__":
    # Python 2.5a2 formats exceptions differently than before, so we
    # add IGNORE_EXCEPTION_DETAIL.  I do not know if this will be
    # fixed or not.
    doctest.testfile("tutorial.txt",
                     optionflags=doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL)
