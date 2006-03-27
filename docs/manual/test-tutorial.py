import doctest
SKIP = doctest.register_optionflag("SKIP")

base = doctest.DocTestRunner
class MyDocTestRunner(base):
    def run(self, test, compileflags=None, out=None, clear_globs=True):
        examples = test.examples[:]
        for ex in test.examples:
            if SKIP in ex.options:
                examples.remove(ex)
        test.examples = examples
        return base.run(self, test, compileflags, out, clear_globs)
doctest.DocTestRunner = MyDocTestRunner

if __name__ == "__main__":
    doctest.testfile("tutorial.txt",
                     optionflags=doctest.ELLIPSIS)
