@echo off

svnmerge merge source
svnmerge merge ctypes

REM revert svnmerge property changes on the directories
svn revert source ctypes

svn diff source ctypes >win64.diff

REM revert all other changes again, now that the diff file is ready.
svn revert -R source ctypes
del svnmerge-commit-message.txt
del source\libffi_msvc\win64.asm
