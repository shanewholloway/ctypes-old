#!/usr/bin/env python
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
    kw["sources"].extend([
        "source/libffi_msvc/types.c",
        "source/libffi_msvc/ffi.c",
        "source/libffi_msvc/prep_cif.c",
        "source/libffi_msvc/win32.c",
        ])
    extensions = [Extension("_ctypes",
                            define_macros=[("CAN_PASS_BY_VALUE", "1")],
                            export_symbols=["DllGetClassObject,PRIVATE",
                                            "DllCanUnloadNow,PRIVATE",
                                            "CopyComPointer"],
                            libraries=["ole32", "user32", "oleaut32"],
                            include_dirs=["source/libffi_msvc"],
                            **kw),
                  Extension("_ctypes_test",
                            libraries=["oleaut32"],
                            sources=["source/_ctypes_test.c"],
                            include_dirs=["source/libffi_msvc"],
                            )
                  ]
    if kw.has_key("depends"):
        kw["depends"].extend(["source/libffi_msvc/ffi.h",
                              "source/libffi_msvc/fficonfig.h",
                              "source/libffi_msvc/ffitarget.h",
                              "source/libffi_msvc/ffi_common.h"])
else:
    include_dirs = ["build/libffi/include",
                    "build/libffi/lib/gcc/3.5.0/include/libffi"]
    library_dirs = ["build/libffi/lib"]
##    if os.path.exists('source/libffi'):
##        include_dirs.append('source/libffi/include')
##        library_dirs.append('source/libffi/lib')
    extra_link_args = []
    if sys.platform == "darwin":
        kw["sources"].append("source/darwin/dlfcn_simple.c")
        extra_link_args.extend(['-read_only_relocs', 'warning'])

    extensions = [Extension("_ctypes",
                            define_macros=[("CAN_PASS_BY_VALUE", "1")],
                            libraries=["ffi"],
                            include_dirs=include_dirs,
                            library_dirs=library_dirs,
                            extra_link_args=extra_link_args,
                            **kw),
                  Extension("_ctypes_test",
                            sources=["source/_ctypes_test.c"],
                            include_dirs=include_dirs,
                            )
                  ]
################################################################
# This section copied from the PyObjC project
if sys.platform == 'darwin':
    # Apple has used build options that don't work with a 'normal' system.
    # Remove '-arch i386' from the LDFLAGS.
    import distutils.sysconfig
    distutils.sysconfig.get_config_vars()
    x = distutils.sysconfig._config_vars['LDSHARED']
    y = x.replace('-arch i386', '')
    if y != x:
        print "Fixing Apple strangeness in Python configuration"
        distutils.sysconfig._config_vars['LDSHARED'] = y

##LIBFFI_SOURCES='libffi-src'
LIBFFI_SOURCES='../gcc/libffi'
if sys.platform != 'darwin' and os.path.exists('/usr/include/ffi.h'):
    # A system with a pre-existing libffi.
    LIBFFI_SOURCES=None

def subprocess(taskName, cmd, validRes=None):
    print "Performing task: %s" % (taskName,)
    res = os.system(cmd)
    validRes = 0
##    fd = os.popen(cmd, 'r')
##    for data in fd.read(256):
##        sys.stdout.write(data)
##        if not data:
##            break

##    res = fd.close()
    if res is not validRes:
        sys.stderr.write("Task '%s' failed [%d]\n"%(taskName, res))
        sys.exit(1)

# We need at least Python 2.2
req_ver = (2, 2)

if sys.version_info < req_ver:
    sys.stderr.write('ctypes: Need at least Python %s\n'%('.'.join(req_ver)))
    sys.exit(1)

if LIBFFI_SOURCES is not None:

    def task_build_libffi(force=0):
        if not os.path.isdir(LIBFFI_SOURCES):
            sys.stderr.write(
                'LIBFFI_SOURCES is not a directory: %s\n'%LIBFFI_SOURCES)
            sys.stderr.write('\tSee Install.txt or Install.html for more information.\n')
            sys.exit(1)

        if not os.path.exists('build'):
            os.mkdir('build')

        if not os.path.exists('build/libffi'):
            os.mkdir('build/libffi')

        if not os.path.exists('build/libffi/BLD'):
            os.mkdir('build/libffi/BLD')

        if force or not os.path.exists('build/libffi/lib/libffi.a'):
            # No pre-build version available, build it now.
            # Do not use a relative path for the build-tree, libtool on
            # MacOS X doesn't like that.
            inst_dir = os.path.join(os.getcwd(), 'build/libffi')
            src_path = os.path.abspath(LIBFFI_SOURCES)

            if ' ' in src_path+inst_dir:
                print >>sys.stderr, "LIBFFI can not build correctly in a path that contains spaces."
                print >>sys.stderr, "This limitation includes the entire path (all parents, etc.)"
                print >>sys.stderr, "Move the ctypes and libffi source to a path without spaces and build again."
                sys.exit(1)

            inst_dir = inst_dir.replace("'", "'\"'\"'")
            src_path = src_path.replace("'", "'\"'\"'")

            subprocess('Building FFI', "cd build/libffi/BLD && '%s/configure' --prefix='%s' --disable-shared --enable-static && make install"%(src_path, inst_dir), None)

    LIBFFI_BASE='build/libffi'
    LIBFFI_CFLAGS=[
        "-isystem", "%s/include"%LIBFFI_BASE,
    ]
    LIBFFI_LDFLAGS=[
        '-L%s/lib'%LIBFFI_BASE, '-lffi',
    ]
    libffi_include = ["include/%s" % LIBFFI_BASE]
    libffi_lib = ["%s/lib" % LIBFFI_BASE]

else:
    def task_build_libffi():
        pass
    LIBFFI_CFLAGS=[]
    LIBFFI_LDFLAGS=['-lffi']


################################################################

packages = ["ctypes"]
package_dir = {}

if sys.platform == "win32":
    packages.append("ctypes.com")
    package_dir["ctypes.com"] = "win32/com"
    packages.append("ctypes.com.samples")
    package_dir["ctypes.com.samples"] = "win32/com/samples"
    packages.append("ctypes.com.tools")
    package_dir["ctypes.com.tools"] = "win32/com/tools"

    packages.append("ctypes.com.samples.server")
    package_dir["ctypes.com.samples.server"] = "win32/com/samples/server"

    packages.append("ctypes.com.samples.server.control")
    package_dir["ctypes.com.samples.server.control"] = "win32/com/samples/server/control"

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
        
        import sys, unittest
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

        # Import all test modules, collect unittest.TestCase classes,
        # and build a TestSuite from them.
        test_suites = []
        for case in self.test_suffixes:
            try:
                mod = __import__(os.path.splitext(self.test_prefix + case)[0])
            except Exception, detail:
                self.warn("Could not import %s (%s)" % (self.test_prefix + case, detail))
                continue
            for name in dir(mod):
                if name.startswith("_"):
                    continue
                o = getattr(mod, name)
                if type(o) is type(unittest.TestCase) and issubclass(o, unittest.TestCase):
                    test_suites.append(unittest.makeSuite(o))

        if test_suites:
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

from distutils.command import build_ext

class my_build_ext(build_ext.build_ext):
    def run(self):
        task_build_libffi(self.force)
        build_ext.build_ext.run(self)

if __name__ == '__main__':
    setup(name="ctypes",
          ext_modules = extensions,
          package_dir = package_dir,
          packages = packages,

          version="0.6.3",
          description="create and manipulate C data types in Python",
          long_description = __doc__,
          author="Thomas Heller",
          author_email="theller@python.net",
          license="MIT License",
          url="http://starship.python.net/crew/theller/ctypes.html",
          platforms=["windows", "Linux", "MacOS X", "Solaris"],

          cmdclass = {'test': test, 'build_py': my_build_py, 'build_ext': my_build_ext},
          **options
          )

## Local Variables:
## compile-command: "python setup.py build -g && python setup.py build install"
## End:
