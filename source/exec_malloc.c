/* Allocate executable memory */
#include <Python.h>
#include <ffi.h>
#include "ctypes.h"

void FreeExecMem(void *p)
{
	PyMem_Free(p);
}

void *MallocExecMem(int size)
{
	return PyMem_Malloc(size);
}

