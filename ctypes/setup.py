#!/usr/bin/env python
#
# $Id$
#
#

"""ctypes is a Python package to create and manipulate C data types in
Python, and to call functions in dynamic link libraries/shared
dlls. It allows wrapping these libraries in pure Python.
"""

# XXX explain LIBFFI_SOURCES
##LIBFFI_SOURCES='libffi-src'
LIBFFI_SOURCES='source/gcc/libffi'

################################################################

import os, sys


from distutils.core import setup, Extension, Command
import distutils.core
from distutils.errors import DistutilsOptionError
from distutils.command import build_py, build_ext, clean
from distutils.dir_util import mkpath

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
    include_dirs = []
    library_dirs = []
    extra_link_args = []
    if sys.platform == "darwin":
        kw["sources"].append("source/darwin/dlfcn_simple.c")
        extra_link_args.extend(['-read_only_relocs', 'warning'])
        include_dirs.append("source/darwin")

    extensions = [Extension("_ctypes",
                            libraries=["ffi"],
                            include_dirs=include_dirs,
                            library_dirs=library_dirs,
                            extra_link_args=extra_link_args,
                            **kw),
                  Extension("_ctypes_test",
                            sources=["source/_ctypes_test.c"])
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

if sys.platform != 'darwin' and os.path.exists('/usr/include/ffi.h') \
       or os.path.exists('/usr/local/include/ffi.h'):
    # A system with a pre-existing libffi.
    LIBFFI_SOURCES=None

if sys.platform == 'win32':
    LIBFFI_SOURCES=None

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
        ('verbosity=', 'V', "verbosity"),
        ]

    def initialize_options(self):
        self.build_base = 'build'
        # these are decided only after 'build_base' has its final value
        # (unless overridden by the user or client)
        self.test_dir = 'unittests'
        self.test_prefix = 'test_'
        self.verbosity = 1

    # initialize_options()

    def finalize_options(self):
        try:
            self.verbosity = int(self.verbosity)
        except ValueError:
            raise DistutilsOptionError, \
                  "verbosity must be an integer"

        build = self.get_finalized_command('build')
        self.build_purelib = build.build_purelib
        self.build_platlib = build.build_platlib

    # finalize_options()

    def run(self):
        import glob, unittest, time
        self.run_command('build')

        mask = os.path.join(self.test_dir, self.test_prefix + "*.py")
        test_files = [os.path.basename(f) for f in glob.glob(mask)]

        self.announce("testing")

        self.testcases = []
        self.ok = self.fail = self.errors = 0
        self.tracebacks = []

        start_time = time.time()
        for t in test_files:
            testcases = self.run_test(os.path.join(self.test_dir, t))
            for case in testcases:
                if self.verbosity > 1:
                    print >> sys.stderr, case
                elif self.verbosity == 1:
                    if case.endswith("ok"):
                        sys.stderr.write(".")
                    elif case.endswith("FAIL"):
                        sys.stderr.write("F")
                    elif case.endswith("ERROR"):
                        sys.stderr.write("E")
                    else:
                        sys.stderr.write("?")
        stop_time = time.time()

        print >> sys.stderr
        for f in self.tracebacks:
            print >> sys.stderr, "=" * 42
            print >> sys.stderr, f[0]
            print >> sys.stderr, "-" * 42
            print >> sys.stderr, "\n".join(f[1:])
            print >> sys.stderr

        print >> sys.stderr, "-" * 70
        print >> sys.stderr, "Ran %d tests in %.3fs" % (len(self.testcases), stop_time - start_time)
        print >> sys.stderr
        if self.fail + self.errors == 0:
            print >> sys.stderr, "OK"
        else:
            if self.errors:
                print >> sys.stderr, "FAILED (failures=%d, errors=%d)" % (self.fail, self.errors)
            else:
                print >> sys.stderr, "FAILED (failures=%d)" % self.fail

    # run()

    def run_test(self, path):
        # Run a test file in a separate process, and parse the output.
        # Collect the results in the ok, fail, error, testcases and
        # tracebacks instance vars.
        # A sequence of testcase names together with their outcome is returned.
        i, o = os.popen4("%s %s -v" % (sys.executable, path))
        i.close()
        cases = []
        while 1:
            line = o.readline()
            if not line:
                break
            line = line.rstrip()
            if line.startswith('test'):
                cases.append(line)
                if line.endswith("ok"):
                    self.ok += 1
                elif line.endswith("FAIL"):
                    self.fail += 1
                elif line.endswith("ERROR"):
                    self.errors += 1
                else: #?
                    self.errors += 1
            elif line == "=" * 70:
                # failure or error
                name = o.readline().rstrip()
                assert o.readline().rstrip() == "-" * 70
                tb = [name]
                while 1:
                    data = o.readline()
                    if not data.rstrip():
                        break
                    tb.append(data.rstrip())
                self.tracebacks.append(tb)
            elif line.rstrip() == '-' * 70:
                pass
            elif line.startswith("Ran "):
                pass
    ##        else:
    ##            print line
        self.testcases.extend(cases)
        return cases

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

class my_build_ext(build_ext.build_ext):
    def run(self):
        self.build_libffi_static()
        build_ext.build_ext.run(self)

    def build_libffi_static(self):
        if LIBFFI_SOURCES == None:
            return
        src_dir = os.path.abspath(LIBFFI_SOURCES)

        # Building libffi in a path containing spaces doesn't work:
        self.build_temp = self.build_temp.replace(" ", "")

        build_dir = os.path.join(self.build_temp, 'libffi')
        inst_dir = os.path.abspath(self.build_temp)
        lib_dir = os.path.abspath(os.path.join(inst_dir, 'lib'))
        inc_dir = os.path.abspath(os.path.join(inst_dir, 'include'))

        for ext in self.extensions:
            ext.include_dirs.append(inc_dir)
            ext.include_dirs.append(os.path.join(lib_dir, "gcc/include/libffi"))
            ext.library_dirs.append(lib_dir)
            # guesswork, for 64-bit platforms
            ext.library_dirs.append(lib_dir + '64')

        if not self.force and os.path.isfile(os.path.join(lib_dir, "libffi.a")):
            return

        mkpath(build_dir)

        cmd = "cd %s && '%s/configure' --prefix='%s' --disable-shared --enable-static && make install" \
              % (build_dir, src_dir, inst_dir)

        print 'Building static FFI library:'
        print cmd
        res = os.system(cmd)
        if res:
            print "Failed"
            sys.exit(res)

# Since we mangle the build_temp dir, we must also do this in the clean command.
class my_clean(clean.clean):
    def run(self):
        self.build_temp = self.build_temp.replace(" ", "")
        clean.clean.run(self)

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

          cmdclass = {'test': test, 'build_py': my_build_py, 'build_ext': my_build_ext, 'clean': my_clean},
          **options
          )

## Local Variables:
## compile-command: "python setup.py build"
## End:
