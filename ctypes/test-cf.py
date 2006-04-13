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

    ("x86-netbsd1",
     # ImportError: _ctypes.so: Undefined PLT symbol "PyGILState_Ensure"
     # Python without threading module???
     # "/usr/pkg/bin/python2.3 -u"
     "~/netbsd/bin/python2.4 -u"),

    ("amd64-linux1", "/usr/bin/python -u"),
    # offline
##    ("amd64-linux2", "/usr/bin/python -u"),

    # Host key verification failed
    ("alpha-linux1", "/usr/bin/python -u"),

    # No route to host:
##    ("ppc-osx1", "/sw/bin/python -u"),

    # No route to host:
##    ("ppc-osx2", "/usr/bin/python -u"),

    # Not python 2.3 or newer, so use my own build of Python 2.4.2:
    ("sparc-solaris1", # "/usr/local/bin/python -u"
     "env PATH=/usr/bin:/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin ~/sparc/bin/python2.4 -u"),
    ("sparc-solaris2", # "/usr/local/bin/python -u"
     "env PATH=/usr/bin:/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin ~/sparc/bin/python2.4 -u"),

    ("openpower-linux1", "python -u")]

import sys, os

try:
    from others import others
except ImportError:
    others = []

for hostname, python in others + hostinfo:
    print "*" * 20, hostname, "*" * 20
    if len(sys.argv) > 1:
        args = " ".join(sys.argv[1:])
    else:
        args = "test -v"

    cmd = "cd $HOME/ctypes; %s setup.py -q build %s" % (python, args)
    print cmd
    if (hostname, python) in hostinfo:
        ret = os.system('ssh -l theller cf-shell.sf.net "ssh %s \'%s\'"' % (hostname, cmd))
    else:
        ret = os.system('ssh -l theller %s \"%s\"' % (hostname, cmd))
    if ret:
        print "(RETCODE %s)" % ret
    print "-" * 50
    print
