# Script to build and test ctypes on the compile-farm servers.
# Accepts the same arguments as setup.py

hostinfo = [
    # Not python 2.3 or newer:
##    ("x86-openbsd1", "/usr/local/bin/python -u"),

    ("x86-solaris1",
     "env PATH=/opt/SUNWspro/bin:/usr/local/bin:/usr/local/sbin:$PATH python -u"),

    ("x86-linux1", "/usr/bin/python -u"),

    ("x86-linux2", "/usr/bin/python -u"),

    # Host key verification failed
    ("x86-freebsd1", "/usr/local/bin/python -u"),

    # ImportError: _ctypes.so: Undefined PLT symbol "PyGILState_Ensure"
    # Python without threading module???
    ("x86-netbsd1", "/usr/pkg/bin/python2.3 -u"),

    ("amd64-linux1", "/usr/bin/python -u"),

    # Same platform as the previous one:
##    ("amd64-linux2", "/usr/bin/python -u"),

    # Host key verification failed
    ("alpha-linux1", "/usr/bin/python -u"),

    # No route to host:
    ("ppc-osx1", "/sw/bin/python -u"),

    # No route to host:
    ("ppc-osx2", "/usr/bin/python -u"),

    # Not python 2.3 or newer:
##    ("sparc-solaris1", "/usr/local/bin/python -u"),
##    ("sparc-solaris2", "/usr/local/bin/python -u"),

    ("openpower-linux1", "python -u")]

import sys, os

for hostname, python in hostinfo:
    print "*" * 20, hostname, "*" * 20
    if len(sys.argv) > 1:
        cmd = "cd ~/ctypes; %s setup.py %s" % (python, " ".join(sys.argv[1:]))
    else:
        cmd = "cd ~/ctypes; %s setup.py -q build_ext -f test -v " % python
    print cmd
    ret = os.system('ssh -l theller cf-shell.sf.net "ssh %s \'%s\'"' % (hostname, cmd))
    if ret:
        print "(RETCODE %s)" % ret
    print "-" * 50
    print
