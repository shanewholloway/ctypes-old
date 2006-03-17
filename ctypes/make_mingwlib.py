"""This script builds the files needed to build Python extensions
with the MingW32 compiler.
"""
# Mostly copied from Martin v. Loewis' Tools\msi\msi.py script
# from the Python distribution.

import sys, os, re
from distutils.spawn import find_executable

# Build the mingw import library, libpythonXY.a
# This requires 'nm' and 'dlltool' executables on your PATH
def build_mingw_lib(lib_file, def_file, dll_file, mingw_lib):
    if os.path.exists(def_file) and os.path.exists(mingw_lib):
        print "make_mingw.lib - nothing to do: files already present"
        return True

    warning = "WARNING: %s - libpythonXX.a not built"
    nm = find_executable('nm')
    dlltool = find_executable('dlltool')

    if not nm or not dlltool:
        print warning % "nm and/or dlltool were not found"
        return False

    nm_command = '%s -Cs %s' % (nm, lib_file)
    dlltool_command = "%s --dllname %s --def %s --output-lib %s" % \
        (dlltool, dll_file, def_file, mingw_lib)
    export_match = re.compile(r"^_imp__(.*) in python\d+\.dll").match

    print "Building", def_file
    f = open(def_file,'w')
    print >>f, "LIBRARY %s" % dll_file
    print >>f, "EXPORTS"

    nm_pipe = os.popen(nm_command)
    for line in nm_pipe.readlines():
        m = export_match(line)
        if m:
            print >>f, m.group(1)
    f.close()
    exit = nm_pipe.close()

    if exit:
        print warning % "nm did not run successfully"
        return False

    print "Building", mingw_lib
    if os.system(dlltool_command) != 0:
        print warning % "dlltool did not run successfully"
        return False

    return True

# Target files (.def and .a) go in PythonXY/libs directory
if __name__ == "__main__":
    srcdir = sys.exec_prefix
    major, minor = sys.version_info[:2]
    lib_file = os.path.join(srcdir, "Libs", "python%s%s.lib" % (major, minor))
    def_file = os.path.join(srcdir, "Libs", "python%s%s.def" % (major, minor))
    dll_file = "python%s%s.dll" % (major, minor)
    mingw_lib = os.path.join(srcdir, "Libs", "libpython%s%s.a" % (major, minor))

    build_mingw_lib(lib_file, def_file, dll_file, mingw_lib)
