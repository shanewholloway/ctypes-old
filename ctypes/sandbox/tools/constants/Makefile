all: constants.py

constants.py: symbols.h make_dump.py dump.h
	make_dump.py symbols.h

symbols.h: dummy.c
	gccxml -D _WIN32_WINNT=0x500 --gccxml-compiler msvc6 --preprocess -dM dummy.c >symbols.h
