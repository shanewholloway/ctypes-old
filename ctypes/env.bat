@echo off
for %%i in (.) do set PYTHONPATH=%%~fi;%%~fi\codegen;%%~fi\codegen\scripts
