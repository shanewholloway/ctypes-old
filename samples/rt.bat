@echo off
@setlocal
@set _exe=c:\python23\python.exe
@if "%1"=="-d" set _exe=c:\python23\python_d.exe

%_exe% Windows\FindFile.py
%_exe% Windows\GetDiskFreeSpaceEx.py
%_exe% Windows\GetSystemInfo.py
%_exe% Windows\VersionInfo.py
%_exe% Windows\test_com.py
%_exe% Windows\test_enumwindows.py
%_exe% Windows\test_enumwindows_mt.py 2
%_exe% Windows\test_word.py

%_exe% test_clib.py
%_exe% test_argcount.py
%_exe% test_strchr.py
%_exe% test_time.py
%_exe% -c "import ctypes; print 'VESION', ctypes.__version__"
