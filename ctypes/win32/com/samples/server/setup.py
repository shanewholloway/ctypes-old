# A setup script for py2exe, to build an exe-file from sum.py
from distutils.core import setup
import py2exe

setup(name='sum', scripts=['sum.py'], version='0.6')
