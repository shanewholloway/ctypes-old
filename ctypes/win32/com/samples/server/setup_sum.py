# A setup script to compile 'sum.py' into an exe file.

from distutils.core import setup
import py2exe

setup(windows=['sum.py'])