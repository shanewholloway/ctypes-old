FFI=${HOME}/ctypes/build/temp.linux-i686-2.4/libffi

CFLAGS=-I ${FFI}/include -I ${FFI} -L ${FFI}/../lib

cls_sint: cls_sint.c
	gcc ${CFLAGS} cls_sint.c -lffi -o cls_sint 
