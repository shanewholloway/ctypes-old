import gccxmltools
from sets import Set

ctypes_names = {
    "int": "c_int",
    "unsigned int": "c_uint",
    "long long int": "c_longlong",
    }

class DependencyResolver(object):
    def __init__(self, objects):
        self.__objects = objects

    def run(self):
        done = Set()
        remaining = Set()

        for o in self.__objects:
            # ONLY THOSE THAT WE DON'T NEED ANYWAY
            if type(o) is gccxmltools.Structure and o.isClass():
                done.add(o)
            elif type(o) is gccxmltools.Constructor:
                done.add(o)
            elif type(o) is gccxmltools.FundamentalType:
                done.add(o)
            elif type(o) is gccxmltools.FunctionType:
                done.add(o)
            elif type(o) is gccxmltools.Function:
                done.add(o)
            elif type(o) is gccxmltools.Method:
                done.add(o)
            else:
                remaining.add(o)

        while remaining:
            resolved = Set()
            for o in remaining:
                deps = Set(o.depends())
                if not deps - done:
                    resolved.add(o)
                    print o
            print
            print "# resolved %d of %d -> %d" % (len(resolved), len(remaining), len(remaining) - len(resolved))
            print
            if not resolved:
                print "%d unresolved deps" % len(remaining)
                return remaining
            done = done | resolved
            remaining = remaining - resolved
##            raw_input("Weiter?")


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
##        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windef.h".split())
        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windows.h".split())

    result = gccxmltools.main()

    p = DependencyResolver(result)
    p.run()
