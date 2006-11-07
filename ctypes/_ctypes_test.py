
def _boot():
    import sys, os, imp
    from distutils.util import get_platform

    plat_specifier = ".%s-%s" % (get_platform(), sys.version[0:3])
    build_dir = os.path.join(os.path.dirname(__file__), 'build', 'lib' + plat_specifier)

    file, path, descr = imp.find_module(__name__, [build_dir])
    imp.load_module(__name__, file, path, descr)

_boot(); del _boot
