#
# $Id$
#
#

"""ctypes is a Python package to create and manipulate C data types in
Python, and to call functions in dynamic link libraries/shared
dlls. It allows wrapping these libraries in pure Python.
"""


from distutils.core import setup, Extension, Command
import distutils.core

import os, sys

kw = {}
kw["sources"] = ["source/_ctypes.c",
                 "source/callbacks.c",
                 "source/callproc.c",
                 "source/stgdict.c",
                 "source/cfield.c"]

# Support the distutils 'depends' option, if available
if hasattr(distutils.core, 'get_distutil_options'):
    # Python 2.3a1
    kw["depends"] = ["source/ctypes.h"]
elif (hasattr(distutils.core, 'extension_keywords') and 
      'depends' in distutils.core.extension_keywords):
    # Python current CVS
    kw["depends"] = ["source/ctypes.h"]


if os.name == "nt":
    extensions = [Extension("_ctypes",
                            define_macros=[("CAN_PASS_BY_VALUE", "1")],
                            export_symbols=["DllGetClassObject,PRIVATE",
                                           "DllCanUnloadNow,PRIVATE"],
                            libraries=["ole32", "user32", "oleaut32"],
                            **kw)
                  ]
else:
    include_dirs = []
    extra_link_args = []
    if sys.platform == "darwin":
        kw["sources"].append("source/darwin/dlfcn_simple.c")
        extra_link_args.extend(['-read_only_relocs', 'warning'])

    extensions = [Extension("_ctypes",
                            libraries=["ffi"],
                            include_dirs=include_dirs,
                            extra_link_args=extra_link_args,
                            **kw),
                  ]

packages = ["ctypes"]
package_dir = {}

if sys.platform == "win32":
    packages.append("ctypes.com")
    package_dir["ctypes.com"] = "win32/com"
    packages.append("ctypes.com.samples")
    package_dir["ctypes.com.samples"] = "win32/com/samples"
    packages.append("ctypes.com.tools")
    package_dir["ctypes.com.tools"] = "win32/com/tools"

################################################################

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
                suite = TEST.get_suite()
            except AttributeError:
                self.announce("\t%s" % (self.test_prefix+case))
                TEST.test(verbose=self.verbose)
            else:
                if suite:
                    test_suites.append(suite)


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

options = {}
if (hasattr(distutils.core, 'setup_keywords') and 
    'classifiers' in distutils.core.setup_keywords):
        kw['classifiers'] = \
                 ['Topic :: Software Development',
                  'Operating System :: MacOS :: MacOS X',
                  'Operating System :: Microsoft :: Windows',
                  'Operating System :: POSIX',
                  'Intended Audience :: Developers',
                  'Development Status :: 3 - Alpha',
                  'Development Status :: 4 - Beta',
                  ]


from distutils.command import build_py

class my_build_py(build_py.build_py):
    def find_package_modules (self, package, package_dir):
        """We extend distutils' build_py.find_package_modules() method
        to include all modules found in the platform specific root
        package directory into the 'ctypes' root package."""
        import glob, sys
        result = build_py.build_py.find_package_modules(self, package, package_dir)
        if package == 'ctypes':
            for pathname in glob.glob(os.path.join(sys.platform, "*.py")):
                modname = os.path.splitext(os.path.basename(pathname))[0]
                result.append(('ctypes', modname, pathname))
        return result

if __name__ == '__main__':
    setup(name="ctypes",
          ext_modules = extensions,
          package_dir = package_dir,
          packages = packages,

          version="0.6.3a",
          description="create and manipulate C data types in Python",
          long_description = __doc__,
          author="Thomas Heller",
          author_email="theller@python.net",
          license="MIT License",
          url="http://starship.python.net/crew/theller/ctypes.html",
          platforms=["windows", "Linux", "MacOS X", "Solaris"],

          cmdclass = {'test': test, 'build_py': my_build_py},
          **options
          )

## Local Variables:
## compile-command: "python setup.py build -g && python setup.py build install"
## End:
