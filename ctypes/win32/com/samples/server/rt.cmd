@echo off
@setlocal
@set _exe=c:\python23\python.exe
@if "%1"=="-d" set _exe=c:\sf\python\dist\src-maint23\PCBuild\python_d.exe

echo "Registering ctypes server"
%_exe% sum.py -regserver
%_exe% sum_user.py local_server
%_exe% test_w32.py local_server
echo "Un-Registering ctypes server"
%_exe% sum.py -unregserver

echo "Registering win32com server"
%_exe% w32server.py --register
%_exe% w32_user.py local_server
%_exe% w32_user.py inproc_server
echo "Un-Registering win32com server"
%_exe% w32server.py --unregister
