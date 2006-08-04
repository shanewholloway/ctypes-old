rem Build the ctypes html pages

set CSS=--stylesheet-path=ctypes.css
set CMD=c:\python24\python -u c:\python24\scripts\rst2html.py %CSS%

%CMD% index.txt > index.html
filter.py ctypes_ref.txt contents.txt reference.txt | %CMD% > reference.html
filter.py ctypes_tut.txt contents.txt tutorial.txt | %CMD% > tutorial.html
