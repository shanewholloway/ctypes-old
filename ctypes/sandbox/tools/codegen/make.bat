@echo off
setlocal
set FLAGS=-s -g -t --stylesheet=default.css
py24 \python24\Scripts\rst2html.py %FLAGS% README.txt README.html