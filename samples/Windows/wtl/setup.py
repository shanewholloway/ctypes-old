# setup.py, config file for distutils

from distutils.core import setup
import py2exe
import glob
import os
import os.path

def globVisit(arg, dirname, names):
    if os.path.split(dirname)[1] == 'CVS': return
    result, pattern = arg
    result.append((dirname, glob.glob(dirname + '/' + pattern)))
    
def globRecursive(path, pattern):
    result = []
    os.path.walk(path, globVisit, (result, pattern))    
    return result

setup(name="cooltest",
      scripts=["test_coolbar.py"],
)

