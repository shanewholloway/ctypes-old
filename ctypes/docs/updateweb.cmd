REM $Id$
make_html -w
scp ../LICENSE.txt default.css ctypes.html theller@starship.python.net:~/public_html/
scp default.css faq.html tutorial.html reference.html theller@starship.python.net:~/public_html/ctypes/
