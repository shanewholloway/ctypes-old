/* Allocate executable memory */
#include <Python.h>
#include <ffi.h>
#include "ctypes.h"

#ifndef MS_WIN32

#include <sys/mman.h>
# if !defined(MAP_ANONYMOUS) && defined(MAP_ANON)
#  define MAP_ANONYMOUS MAP_ANON
# endif

#endif

void FreeExecMem(void *p)
{
#ifdef MS_WIN32
	PyMem_Free(p);
#endif
}

void *MallocExecMem(int size)
{
#ifdef MS_WIN32
	return PyMem_Malloc(size);
#else
	void *page;
	page = mmap(NULL,
		    size,
		    PROT_READ | PROT_WRITE | PROT_EXEC,
		    MAP_PRIVATE | MAP_ANONYMOUS,
		    -1,
		    0);
	if (page == (void *)MAP_FAILED)
		return NULL;
	return page;
#endif
}

