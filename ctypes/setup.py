#
# $Id$
#
#

"""ctypes is a Python module allowing to create and manipulate C data
types in Python. These can then be passed to C-functions loaded from
dynamic link libraries."""

from distutils.core import setup, Extension, Command
import distutils.core

import os

kw = {}
kw["sources"] = ["source/_ctypes.c",
                 "source/callbacks.c",
                 "source/callproc.c"]

# Support the distutils 'depends' option, if availabale
if hasattr(distutils.core, 'get_distutil_options'):
    kw["depends"] = ["source/ctypes.h"]
                  

if os.name == "nt":
    extensions = [Extension("_ctypes",
                            export_symbols=["DllGetClassObject,PRIVATE",
                                            "DllCanUnloadNow,PRIVATE"],
                            libraries=["ole32"],
                            **kw)
                  ]
else:
    extensions = [Extension("_ctypes",
                            libraries=["ffi"],
                            **kw),
                  ]

class test(Command):
    # Original version of this class posted
    # by Berthold Hoellmann to distutils-sig@python.org
    description = "test the distribution prior to install"

    user_options = [
        ('test-dir=', None,
         "directory that contains the test definitions"),
        ('test-prefix=', None,
         "prefix to the testcase filename"),
        ('test-suffixes=', None,
         "a list of suffixes used to generate names the of the testcases")
        ]

    def initialize_options(self):
        self.build_base = 'build'
        # these are decided only after 'build_base' has its final value
        # (unless overridden by the user or client)
        self.test_dir = 'unittests'
        self.test_prefix = 'test_'
        self.test_suffixes = None

    # initialize_options()

    def finalize_options(self):
        if self.test_suffixes is None:
            self.test_suffixes = []
            pref_len = len(self.test_prefix)
            for file in os.listdir(self.test_dir):
                if (file[-3:] == ".py" and
                    file[:pref_len]==self.test_prefix):
                    self.test_suffixes.append(file[pref_len:-3])

        build = self.get_finalized_command('build')
        self.build_purelib = build.build_purelib
        self.build_platlib = build.build_platlib

    # finalize_options()


    def run(self):
        
        import sys
        # Invoke the 'build' command to "build" pure Python modules
        # (ie. copy 'em into the build tree)
        self.run_command('build')

        # remember old sys.path to restore it afterwards
        old_path = sys.path[:]

        # extend sys.path
        sys.path.insert(0, self.build_purelib)
        sys.path.insert(0, self.build_platlib)
        sys.path.insert(0, self.test_dir)
        
        self.announce("testing")
        # build include path for test

        test_suites = []

        for case in self.test_suffixes:
            TEST = __import__(self.test_prefix+case,
                              globals(), locals(),
                              [''])

            # Test modules must either expose a test() function which
            # will be called to run the test, or a get_suite() function
            # which returns a TestSuite.
            try:
                test_suites.append(TEST.get_suite())
            except AttributeError:
                self.announce("\t%s" % (self.test_prefix+case))
                TEST.test(verbose=self.verbose)

        if test_suites:
            import unittest
            suite = unittest.TestSuite(test_suites)
            self.announce("running unittests")

            runner = unittest.TextTestRunner(verbosity=self.verbose)
            runner.run(suite)

        # restore sys.path
        sys.path = old_path[:]

    # run()

# class test

##from distutils.command import build_py

## a class which will allow to distribute packages *and*
## modules with one setup script, currently unused.
##class my_build_py(build_py.build_py):
##    def run (self):
##        if not self.py_modules and not self.packages:
##            return

##        if self.py_modules:
##            self.build_modules()
##        if self.packages:
##            self.build_packages()

##        self.byte_compile(self.get_outputs(include_bytecode=0))
##    # run ()

if __name__ == '__main__':
    setup(name="ctypes",
          ext_modules = extensions,
##          packages = ["ctcom"],
          py_modules = ["ctypes"],
          version="0.4.0",
          description="create and manipulate C data types in Python",
          long_description = __doc__,
          author="Thomas Heller",
          author_email="theller@python.net",
          license="MIT License",
          url="http://starship.python.net/crew/theller/ctypes.html",
          platforms=["windows", "linux"],

          cmdclass = {'test': test}
          )

## Local Variables:
## compile-command: "python setup.py build -g && python setup.py build install"
## End:
