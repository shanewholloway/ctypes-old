REM $Id$
make_html -w
copy tutorial.html ctypes.html
copy ..\dist\ctypes-0.2.0.zip .
copy ..\dist\ctypes-0.2.0.win32-py2.2.exe .
scp ctypes-0.2.0.zip ctypes-0.2.0.win32-py2.2.exe  default.css reference.html ctypes.html theller@starship.python.net:~/public_html/
del ctypes-0.2.0.zip
del ctypes-0.2.0.win32-py2.2.exe
del *.html
