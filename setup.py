#!/usr/bin/env python
#
# $Id$
#
#

"""ctypes is a Python package to create and manipulate C data types in
Python, and to call functions in dynamic link libraries/shared
dlls. It allows wrapping these libraries in pure Python.
"""

LIBFFI_SOURCES='source/gcc/libffi'

__version__ = "0.9.2"

################################################################

import os, sys

if sys.version_info < (2, 3):
    raise Exception, "ctypes %s requires Python 2.3 or better" % __version__

from distutils.core import setup, Extension, Command
import distutils.core
from distutils.errors import DistutilsOptionError
from distutils.command import build_py, build_ext, clean
from distutils.command import install_data
from distutils.dir_util import mkpath
from distutils.util import get_platform

################################################################
# Manipulate the environment for the build process.
#
if sys.platform == 'darwin':
    # This section copied from the PyObjC project
    # Apple has used build options that don't work with a 'normal' system.
    # Remove '-arch i386' from the LDFLAGS.
    import distutils.sysconfig
    distutils.sysconfig.get_config_vars()
    x = distutils.sysconfig._config_vars['LDSHARED']
    y = x.replace('-arch i386', '')
    if y != x:
        print "Fixing Apple strangeness in Python configuration"
        distutils.sysconfig._config_vars['LDSHARED'] = y

if get_platform() in ["solaris-2.9-sun4u", "linux-x86_64"]:
    os.environ["CFLAGS"] = "-fPIC"

################################################################
# Additional and overridden distutils commands
#
class test(Command):
    # Original version of this class posted
    # by Berthold Hoellmann to distutils-sig@python.org
    description = "test the distribution prior to install"

    user_options = [
        ('test-dirs=', None,
         "comma-separated list of directories that contain the test definitions"),
        ('test-prefix=', None,
         "prefix to the testcase filename"),
        ('verbosity=', 'V', "verbosity"),
        ]

    def initialize_options(self):
        self.build_base = 'build'
        # these are decided only after 'build_base' has its final value
        # (unless overridden by the user or client)
        self.test_prefix = 'test_'
        self.verbosity = 1
        if sys.platform == "win32":
            self.test_dirs = r"unittests,unittests\com"
        else:
            self.test_dirs = "unittests"

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

        self.test_dirs = self.test_dirs.split(",")

    # finalize_options()

    def extend_path(self):
        # We must add the current directory to $PYTHONPATH for the unittests
        # running as separate processes
        pypath = os.environ.get("PYTHONPATH")
        if pypath:
            pypath = pypath.split(os.pathsep) + []
        else:
            pypath = []
        if os.getcwd() in pypath:
            return
        os.environ["PYTHONPATH"] = os.pathsep.join(pypath)

    def run(self):
        import glob, unittest, time
        self.run_command('build')

        for direct in self.test_dirs:
            mask = os.path.join(direct, self.test_prefix + "*.py")
            test_files = glob.glob(mask)

            print "=== Testing in '%s' ===" % direct
            self.extend_path()

            self.testcases = []
            self.ok = self.fail = self.errors = 0
            self.tracebacks = []

            start_time = time.time()
            for t in test_files:
                testcases = self.run_test(t)
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
            print >> sys.stderr, "Ran %d tests in %.3fs" % (len(self.testcases),
                                                            stop_time - start_time)
            print >> sys.stderr
            if self.fail + self.errors == 0:
                print >> sys.stderr, "OK"
            else:
                if self.errors:
                    print >> sys.stderr, "FAILED (failures=%d, errors=%d)" % (self.fail,
                                                                              self.errors)
                else:
                    print >> sys.stderr, "FAILED (failures=%d)" % self.fail

    # run()

    def run_test(self, path):
        # Run a test file in a separate process, and parse the output.
        # Collect the results in the ok, fail, error, testcases and
        # tracebacks instance vars.
        # A sequence of testcase names together with their outcome is returned.
        if self.verbosity > 1:
            print "Running '%s run_remote_test.py %s'" % (sys.executable, path)
        os.system("%s run_remote_test.py %s" % (sys.executable, path))
        cases = []
        o = open("test.output")
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
                    self.tracebacks.append([line, "Crashed"])
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

def find_file_in_subdir(dirname, filename):
    # if <filename> is in <dirname> or any subdirectory thereof,
    # return the directory name, else None
    for d, _, names in os.walk(dirname):
        if filename in names:
            return d
    return None

class my_build_ext(build_ext.build_ext):
    def finalize_options(self):
        if self.debug is None:
            import imp
            self.debug = ('_d.pyd', 'rb', imp.C_EXTENSION) in imp.get_suffixes()
        build_ext.build_ext.finalize_options(self)

    # First build a static libffi library, then build the _ctypes extension.
    def run(self):
        self.build_libffi_static()
        build_ext.build_ext.run(self)

    def fix_extension(self, inst_dir):
        incdir = find_file_in_subdir(os.path.join(inst_dir, "include"), "ffi.h")
        if not incdir:
            return 0
        libdir = find_file_in_subdir(os.path.join(inst_dir, "lib"), "libffi.a") or \
                 find_file_in_subdir(os.path.join(inst_dir, "lib64"), "libffi.a")
        if not libdir:
            return 0
        incdir_2 = find_file_in_subdir(os.path.join(inst_dir, "lib"), "ffitarget.h")
        if not incdir_2:
            return 0
        for ext in self.extensions:
            if ext.name == "_ctypes":
                ext.include_dirs.append(incdir)
                ext.include_dirs.append(incdir_2)
                ext.library_dirs.append(libdir)
	return 1

    def build_libffi_static(self):
        if sys.platform == "win32":
            return
        if LIBFFI_SOURCES == None:
            return
        src_dir = os.path.abspath(LIBFFI_SOURCES)

        # Building libffi in a path containing spaces doesn't work:
        self.build_temp = self.build_temp.replace(" ", "")

        build_dir = os.path.join(self.build_temp, 'libffi')
        inst_dir = os.path.abspath(self.build_temp)

        if not self.force and self.fix_extension(inst_dir):
            return

        mkpath(build_dir)
	config_args = ["--disable-shared",
		       "--enable-static",
		       "--enable-multilib=no",
		       "--prefix='%s'" % inst_dir,
        ]

        cmd = "cd %s && '%s/configure' %s && make install" \
              % (build_dir, src_dir, " ".join(config_args))

        print 'Building static FFI library:'
        print cmd
        res = os.system(cmd)
        if res:
            print "Failed"
            sys.exit(res)

        assert self.fix_extension(inst_dir), "Could not find libffi after building it"

# Since we mangle the build_temp dir, we must also do this in the clean command.
class my_clean(clean.clean):
    def run(self):
        self.build_temp = self.build_temp.replace(" ", "")
        clean.clean.run(self)

class my_install_data(install_data.install_data):
     """A custom install_data command, which will install it's files
     into the standard directories (normally lib/site-packages).
     """
     def finalize_options(self):
         if self.install_dir is None:
             installobj = self.distribution.get_command_obj('install')
             self.install_dir = installobj.install_lib
         print 'Installing data files to %s' % self.install_dir
         install_data.install_data.finalize_options(self)

################################################################
# Specify the _ctypes extension
#
kw = {}
# common source files
kw["sources"] = ["source/_ctypes.c",
                 "source/callbacks.c",
                 "source/callproc.c",
                 "source/stgdict.c",
                 "source/cfield.c"]

# common header file
kw["depends"] = ["source/ctypes.h"]

if sys.platform == "win32":
    kw["sources"].extend([
        # types.c is no longer needed, ffi_type defs are in cfield.c
        "source/libffi_msvc/ffi.c",
        "source/libffi_msvc/prep_cif.c",
        "source/libffi_msvc/win32.c",
        ])
    extensions = [Extension("_ctypes",
                            export_symbols=["DllGetClassObject,PRIVATE",
                                            "DllCanUnloadNow,PRIVATE"],
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
# the ctypes package
#
packages = ["ctypes"]
package_dir = {}

################################################################
# the ctypes.com package
#
if sys.platform == "win32":
    packages.append("ctypes.com")
    package_dir["ctypes.com"] = "win32/com"

    packages.append("ctypes.com.tools")
    package_dir["ctypes.com.tools"] = "win32/com/tools"

################################################################
# options for distutils, and ctypes.com samples
#
setup_options = {}

if sys.platform == 'win32':
    # Use different MANIFEST templates, to minimize the distribution
    # size.  Also, the MANIFEST templates behave differently on
    # Windows and Linux (distutils bug?).
    # Finally, force rebuilding the MANIFEST file

    setup_options["sdist"] = {"template": "MANIFEST.windows.in", "force_manifest": 1}

    import glob
    data_files = [("ctypes/com/samples",
                   glob.glob("win32/com/samples/*.py") +
                   glob.glob("win32/com/samples/*.txt")),

                  ("ctypes/com/samples/server",
                   glob.glob("win32/com/samples/server/*.py") +
                   glob.glob("win32/com/samples/server/*.txt")),

                  ("ctypes/com/samples/server/control",
                   glob.glob("win32/com/samples/server/control/*.py") +
                   glob.glob("win32/com/samples/server/control/*.txt") +
                   glob.glob("win32/com/samples/server/control/*.html")),

                  ("ctypes/com/samples/server/IExplorer",
                   glob.glob("win32/com/samples/server/IExplorer/*.py") +
                   glob.glob("win32/com/samples/server/IExplorer/*.txt") +
                   glob.glob("win32/com/samples/server/IExplorer/*.html")),
                  ]

else:
    setup_options["sdist"] = {"template": "MANIFEST.other.in", "force_manifest": 1}
    data_files = []

################################################################
# pypi classifiers
#
classifiers = [
    'Development Status :: 4 - Beta',
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: C',
    'Programming Language :: Python',
    'Topic :: Software Development :: Libraries :: Python Modules',
    ]

################################################################
# main section
#
if __name__ == '__main__':
    setup(name="ctypes",
          ext_modules = extensions,
          package_dir = package_dir,
          packages = packages,
          data_files = data_files,

          classifiers = classifiers,

          version=__version__,
          description="create and manipulate C data types in Python",
          long_description = __doc__,
          author="Thomas Heller",
          author_email="theller@python.net",
          license="MIT License",
          url="http://starship.python.net/crew/theller/ctypes.html",
          platforms=["windows", "Linux", "MacOS X", "Solaris", "FreeBSD"],
          
          cmdclass = {'test': test, 'build_py': my_build_py, 'build_ext': my_build_ext,
                      'clean': my_clean, 'install_data': my_install_data},
          options = setup_options
          )

## Local Variables:
## compile-command: "python setup.py build"
## End:
