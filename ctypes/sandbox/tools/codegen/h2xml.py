"""h2xml - convert C include file(s) into an xml file by running gccxml."""
import sys, os, tempfile

if sys.platform == "win32":

    def _locate_gccxml():
        import _winreg
        for subkey in (r"Software\gccxml", r"Software\Kitware\GCC_XML"):
            for root in (_winreg.HKEY_CURRENT_USER, _winreg.HKEY_LOCAL_MACHINE):
                try:
                    hkey = _winreg.OpenKey(root, subkey, 0, _winreg.KEY_READ)
                except WindowsError, detail:
                    if detail.errno != 2:
                        raise
                else:
                    return _winreg.QueryValueEx(hkey, "loc")[0] + r"\bin"

    loc = _locate_gccxml()
    if loc:
        os.environ["PATH"] = loc

################################################################

class CompilerError(Exception):
    pass

# Create a C file containing #includes to the specified filenames.
# Run GCCXML to create an XML file, and return the xml filename.
def run_gccxml(fnames, options, verbose=0, xml_file=None):
    # fnames is the sequence of include files
    # options is seuqence of strings containing command line options for GCCXML
    # verbose - integer specifying the verbosity
    #
    # returns the filename of the generated XML file

    # write a temporary C file
    handle, c_file = tempfile.mkstemp(suffix=".c", text=True)
    if verbose:
        print >> sys.stderr, "writing temporary C source file %s" % c_file
##    os.write(handle, 'extern "C" {\n');
    for fname in fnames:
        os.write(handle, '#include <%s>\n' % fname)
##    os.write(handle, '}');
    os.close(handle)

    if xml_file is None:
        handle, xml_file = tempfile.mkstemp(suffix=".xml", text=True)
        os.close(handle)

    if options:
        options = " ".join(options)
    else:
        options = ""

    try:
        if verbose:
            print >> sys.stderr, r"gccxml %s %s -fxml=%s" % (options, c_file, xml_file)
        i, o = os.popen4(r"gccxml %s %s -fxml=%s" % (options, c_file, xml_file))
        i.close()
        sys.stderr.write(o.read())
        retval = o.close()
        if retval:
            raise CompilerError, "gccxml returned error %s" % retval
        return xml_file
    finally:
        if verbose:
            print >> sys.stderr, "Deleting temporary file %s" % c_file
        os.remove(c_file)

################################################################

def main():
    from optparse import OptionParser

    def add_option(option, opt, value, parser):
        parser.values.gccxml_options.append("%s %s" % (opt, value))

    parser = OptionParser()
##    parser.add_option("-h", action="help")
    parser.add_option("-v", "--verbose",
                      dest="verbose",
                      action="store_true",
                      default=False)

    parser.add_option("-D",
                      type="string",
                      action="callback",
                      callback=add_option,
                      dest="gccxml_options",
                      help="macros to define",
                      metavar="defines",
                      default=[])
    parser.add_option("-U",
                      type="string",
                      action="callback",
                      callback=add_option,
                      help="macros to undefine",
                      metavar="defines")

    parser.add_option("-I",
                      type="string",
                      action="callback",
                      callback=add_option,
                      dest="gccxml_options",
                      help="include directories",
                      metavar="defines")

    parser.add_option("-o",
                      dest="xml_file",
                      help="XML output filename",
                      default=None)
    options, files = parser.parse_args()

    if not files:
        print "Error: no files to process"
        print >> sys.stderr, __doc__
        return 1

    try:
        xmlfile = run_gccxml(files, options.gccxml_options, options.verbose, options.xml_file)
    except CompilerError, detail:
        sys.exit(1)

    if options.xml_file is None:
        if options.verbose:
            print >> sys.stderr, "Deleting temporary file %s" % xmlfile
        os.remove(xmlfile)

if __name__ == "__main__":
    main()
