import gccxmltools

class EnumCodeGenerator(gccxmltools.Visitor):

    def __init__(self, *args, **kw):
        super(EnumCodeGenerator, self).__init__(*args, **kw)
        self.__enums = {} # <enum name>: <enum code>
        self.__typedefs = {} # <enum name>: [<other names>]

    def Enumeration(self, enum):
        # generate the ctypes code for an enumeration.
        code = ["class %s(c_int):" % enum.name]
        code += ["    %s = %s" % pair for pair in enum.values]
        self.__enums[enum.name] = "\n".join(code)

    def Typedef(self, td):
        # if this is a typedef for an enum, record it
        if type(td.typ) is gccxmltools.Enumeration:
            othernames = self.__typedefs.setdefault(td.typ.name, [])
            othernames.append(td.name)

    def get_code(self):
        # return a string containing the ctypes Python code for all enums
        result = []
        for name, code in self.__enums.iteritems():
            result.append(code)
            other_names = self.__typedefs.get(name, [])
            for othername in other_names:
                result.append("%s = %s" % (othername, name))
            result.append("")
        return "\n".join(result)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        sys.argv.extend("-D NONAMELESSUNION -D _WIN32_WINNT=0x500 -c msvc6 -o- windows.h".split())

    result = gccxmltools.main()

    p = EnumCodeGenerator(result)
    p.go()
    print p.get_code()
