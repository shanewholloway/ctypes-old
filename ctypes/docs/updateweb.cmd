REM $Id$
make_html -w
scp ../LICENSE.txt default.css ctypes.html theller@starship.python.net:~/public_html/
scp default.css changes.html com.html faq.html index.html sum_sample.html tutorial.html reference.html theller@starship.python.net:~/public_html/ctypes/
