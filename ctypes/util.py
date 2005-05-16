import os, re, tempfile

if os.name == "posix":

    def findLib_gcc(name):
        expr = '[^\(\)\s]*lib%s\.[^\(\)\s]*' % name
        cmd = 'if type gcc &>/dev/null; then CC=gcc; else CC=cc; fi;' \
              '$CC -Wl,-t -o /dev/null 2>&1 -l' + name
        try:
            fdout, outfile =  tempfile.mkstemp()
            fd = os.popen(cmd)
            trace = fd.read()
            err = fd.close()
        finally:
            try:
                os.unlink(outfile)
            except OSError, e:
                if e.errno != errno.ENOENT:
                    raise
        res = re.search(expr, trace)
        if not res:
            return None
        return res.group(0)

    def findLib_ld(name):
        expr = '/[^\(\)\s]*lib%s\.[^\(\)\s]*' % name
        res = re.search(expr, os.popen('/sbin/ldconfig -p 2>/dev/null').read())
        if not res:
            return None
        return res.group(0)

    def get_soname(f):
        cmd = "objdump -p -j .dynamic 2>/dev/null " + f
        res = re.search(r'\sSONAME\s+([^\s]+)', os.popen(cmd).read())
        if not res:
            return f
        return res.group(1)

    def findLib(name):
        lib = findLib_ld(name)
        if not lib:
            lib = findLib_gcc(name)
            if not lib:
                return [name]
        return [get_soname(lib)]
