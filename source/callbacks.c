/*
 * Copyright 1999-2002, Thomas Heller
 *
 * $Id$
 *
 */

/*
 ToDo:
 */
#include "Python.h"
#include "ctypes.h"

#ifdef MS_WIN32
#include <windows.h>
#else
#include <ffi.h>
#define __stdcall /* */
#endif

static PyInterpreterState *g_interp;	/* need this to create new thread states */

static void EnterPython(char *msg)
{
	PyThreadState *pts;
	PyEval_AcquireLock();
	pts = PyThreadState_New(g_interp);
	if (!pts)
		Py_FatalError("wincall: Could not allocate ThreadState");
	if (NULL != PyThreadState_Swap(pts))
		Py_FatalError("wincall (EnterPython): thread state not == NULL?");
}

static void LeavePython(char *msg)
{
	PyThreadState *pts = PyThreadState_Swap(NULL);
	if (!pts)
		Py_FatalError("wincall (LeavePython): ThreadState is NULL?");
	PyThreadState_Clear(pts);
	PyThreadState_Delete(pts);
	PyEval_ReleaseLock();
}

#define ENTER_PYTHON(msg)		EnterPython(msg)
#define LEAVE_PYTHON(msg)		LeavePython(msg)

/********************************************************************************
 *
 * callback objects: definition
 */

THUNK AllocFunctionCallback(PyObject *callable,
			    int nArgBytes,
			    PyObject *converters,
			    int stdcall);


#ifdef MS_WIN32
staticforward THUNK AllocCallback(PyObject *callable,
				  int nArgBytes,
				  PyObject *converters,
				  DWORD RouterAddress,
				  int stdcall);

static int __stdcall CallPythonVTableEntry(PyObject *callable,
					   PyObject *converters,
					   void **pArgs);
#endif

static int __stdcall CallPythonObject(PyObject *callable,
				      PyObject *converters,
				      void **pArgs);

static void
PrintError(char *msg, ...)
{
	char buf[512];
	PyObject *f = PySys_GetObject("stderr");
	va_list marker;

	va_start(marker, msg);
	vsnprintf(buf, sizeof(buf), msg, marker);
	va_end(marker);
	if (f)
		PyFile_WriteString(buf, f);
	PyErr_Print();
}

/******************************************************************************
 *
 * Call the python object with all arguments
 *
 */
static int __stdcall CallPythonObject(PyObject *callable,
				       PyObject *converters, void **pArgs)
{
	int i;
	PyObject *result;
	PyObject *arglist;
	PyObject *p;
	int nArgs;
	int retcode;

	nArgs = PySequence_Length(converters);
	/* Hm. What to return in case of error?
	   For COM, 0xFFFFFFFF seems better than 0.
	*/
	retcode = 0xFFFFFFFF;

	ENTER_PYTHON("CallPythonObject");
	arglist = PyTuple_New(nArgs);
	for (i = 0; i < nArgs; ++i) {
		/* Note: new reference! */
		PyObject *cnv = PySequence_GetItem(converters, i);
		StgDictObject *dict;
		if (cnv)
			dict = PyType_stgdict(cnv);

		if (!cnv) {
			PrintError("Getting argument converter %d\n", i);
			goto Done;
		} else if (dict) {
			CDataObject *obj = (CDataObject *)PyObject_CallFunctionObjArgs(cnv, NULL);
			if (!obj) {
				PrintError("create argument %d:\n", i);
				goto Done;
			}
			if (!CDataObject_Check(obj)) {
				Py_DECREF(obj);
				PrintError("unexpected result of create argument %d:\n", i);
				goto Done;
			}
			memcpy(obj->b_ptr, pArgs, dict->size);
			pArgs += dict->size / sizeof(int);
			PyTuple_SET_ITEM(arglist, i, (PyObject *)obj);
		} else if (PyString_Check(cnv)) {
			/* XXX Here shows a bug, which also shows up somewhere else:
			   Look for PyBuild_Value().
			   PyBuild_Value, when passed a 'h' format tag, for example,
			   happily builds int's larger than short!
			   
			   Cannot fix it now, but should later.
			*/
			p = Py_BuildValue(PyString_AS_STRING(cnv), *pArgs++);
			if (!p) {
				PrintError("argument %d:\n", i);
				goto Done;
			}
			PyTuple_SET_ITEM(arglist, i, p); /* consumes 'p' */
		} else if (PyCallable_Check(cnv)) {
			PyObject *obj = PyObject_CallFunction(cnv, "i", *pArgs++);
			if (!obj) {
				PrintError("Converter failed on argument %d:\n", i);
				goto Done;
			}
			PyTuple_SET_ITEM(arglist, i, obj);
		} else {
			PyErr_SetString(PyExc_TypeError,
					"cannot build parameter");
			PrintError("Parsing argument %d\n", i);
			goto Done;
		}
		/* XXX error handling! */
	}
	result = PyObject_CallObject(callable, arglist);
	if (!result) {
		PrintError("CallObject\n");
	} else {
		if ((result != Py_None)
		    && !PyArg_Parse(result, "i", &retcode))
			PyErr_Print();
	}
  Done:
	Py_DECREF(arglist);
	LEAVE_PYTHON("CallPythonObject");
	return retcode;
}

#ifdef MS_WIN32
/******************************************************************************
 *
 * Call the python object with all arguments EXCEPT the first one,
 * which is the this pointer
 *
 */
static int __stdcall CallPythonVTableEntry(PyObject *callable,
					    PyObject *converters, void **pArgs)
{
	int i;
	PyObject *result;
	PyObject *arglist;
	PyObject *p;
	/* Number of arguments of callable function */
	int nArgs = PySequence_Length(converters);
	int retcode = 0;

	ENTER_PYTHON("CallPythonVTableEntry");
	arglist = PyTuple_New(nArgs);
	for (i = 0; i < nArgs; ++i) {
		/* Note: new reference! */
		PyObject *cnv = PySequence_GetItem(converters, i);
		if (PyString_Check(cnv)) {
			p = Py_BuildValue(PyString_AS_STRING(cnv), pArgs[i+1]);
			PyTuple_SET_ITEM(arglist, i, p);
		} else {	/* it is callable, has been checked before! */
			PyObject *kw = Py_BuildValue("{s:i}", "_buffer_", pArgs[i+1]);
			PyObject *obj = PyEval_CallObjectWithKeywords(cnv, NULL, kw);
			Py_DECREF(kw);
			PyTuple_SET_ITEM(arglist, i, obj);
		}
		/* XXX error handling! */
	}
	result = PyObject_CallObject(callable, arglist);
	Py_DECREF(arglist);	/* items??? */
	if (!result) {
		PyErr_Print();
	} else {
		if (!PyArg_Parse(result, "i", &retcode))
			PyErr_Print();
	}
	LEAVE_PYTHON("CallPythonVTableEntry");
	return retcode;
}


#define NOSTACKFRAME
//#define BREAKPOINTS

#pragma warning( disable : 4035 )	/* Disable warning about no return value */
/*
 * Callbacks are small blocks of code which create an interface between code
 * using different calling conventions.
 * In this case, an interface from __stdcall C-functions to python
 * callable objects is provided. Note that __stdcall is used to call
 * win32 api functions, and also for callback functions.
 *
 * Callbacks are created by allocating some memory, copying the bytes from this
 * template into it, and configuring the callback by setting the number of
 * argument bytes and the address of the python object.
 * For copying and configuring the callback we need the addresses of some
 * assembler labels. These addresses are returned when the CallbackTemplate
 * is called directly, without beeing configured.
 */
static int __declspec ( naked ) CallbackTemplate(DWORD arg)
{
    /* This function will be called with the __stdcall calling convention:
     * Arguments are pushed in right to left order onto the stack.
     * Callee has to remove its own arguments from stack.
     */
    _asm {
      CallbackStart:
#ifdef BREAKPOINTS
	int		3
#endif
#ifndef NOSTACKFRAME
	push	ebp
	mov	ebp, esp
#endif
/* Trick for position independent code, transferring NumberArgs into ecx */
        call	_1
_1:
	pop	eax
	add	eax, OFFSET NumberArgs
	sub	eax, OFFSET _1
	mov	ecx, [eax]

/* Trick for position independent code, transferring CallAddress into edx */
	call	_2
_2:
	pop	eax
	add	eax, OFFSET CallAddress
	sub	eax, OFFSET _2
	mov	edx, [eax]

	or	edx, edx
	jz	ReturnInfo

	call	_2a
_2a:
	pop	eax
	add	eax, OFFSET ConvertersAddress
	sub	eax, OFFSET _2a
	mov	ecx, [eax]

#ifdef NOSTACKFRAME
	mov	eax, esp
	add	eax, 4		// return address is on stack
#else
        mov	eax, ebp
	add	eax, 8		// return address and ebp is on stack
#endif
	/* push arguments in reverse order
	 * Register contents:
	 *	EAX: Pointer to arguments
	 *	ECX: Pointer to converters
	 *	EDX: Pointer to python callable object
	 */
	push	eax
	push	ecx
	push	edx

/* Trick for position independent code, transferring CallAddress into eax */
	call	_3
_3:
	pop	eax
	add	eax, OFFSET RouterAddress
	sub	eax, OFFSET _3

	call[eax]

#ifndef NOSTACKFRAME
	mov	esp, ebp
	pop	ebp
#endif 
#ifdef BREAKPOINTS
	int	3
#endif
/* For __stdcall functions: */
	_emit	0xC2	/* ret ... */
/* __cdecl functions would require a simple 'ret' 0xC3 here... */
/*
 * Static storage for four DWORDS, containing the callbacks number of arguments
 * and the address of the python object to call
 * Note that NumberArgs must follow immediately the 'ret' instruction
 * above!
 */
NumberArgs:
	_emit	0
	_emit	0
	_emit	0
	_emit	0
ConvertersAddress:
	_emit	0
	_emit	0
	_emit	0
	_emit	0
CallAddress:			/* Python object to call */
	_emit	0
	_emit	0
	_emit	0
	_emit	0
RouterAddress:			/* C-function to route call */
	_emit	0
	_emit	0
	_emit	0
	_emit	0
CallbackEnd:

ReturnInfo:
	mov	eax, OFFSET CallbackStart
	mov	edx, OFFSET CallbackEnd

#ifndef NOSTACKFRAME
	mov	esp, ebp
	pop	ebp
#endif
	ret	4
    }
}
#pragma warning( default : 4035 )	/* Reenable warning about no return value */

/*****************************************************************************/

typedef struct {
    BYTE *pStart;
    BYTE *pEnd;
} CALLBACKINFO;

static CALLBACKINFO ti;

/*
 * Allocate a callback and configure it
 */
static THUNK AllocCallback(PyObject *callable, int nArgBytes,
			   PyObject *converters, DWORD RouterAddress,
			   int stdcall)
{
	BYTE *pCallback, *pNargBytes, *pConverters, *pCalladdr, *pRouter;

	pCallback = malloc(ti.pEnd - ti.pStart);
	memcpy(pCallback, ti.pStart, ti.pEnd - ti.pStart);
	pNargBytes = pCallback +(ti.pEnd - ti.pStart) - 16;
	pConverters = pCallback + (ti.pEnd - ti.pStart) - 12;
	pCalladdr = pCallback + (ti.pEnd - ti.pStart) - 8;
	pRouter = pCallback + (ti.pEnd - ti.pStart) - 4;
	*(DWORD *)pNargBytes = nArgBytes;
	if (stdcall)
		((BYTE *)pNargBytes)[-1] = 0xC2; /* ret <args>: for stdcall */
	else
		((BYTE *)pNargBytes)[-1] = 0xC3; /* ret: for cdecl */
	*(DWORD *)pConverters = (DWORD)converters;
	*(DWORD *)pCalladdr = (DWORD)callable;
	*(DWORD *)pRouter = RouterAddress;
	return (THUNK)pCallback;
}

THUNK AllocFunctionCallback(PyObject *callable,
			    int nArgBytes,
			    PyObject *converters,
			    int stdcall)
{
	return AllocCallback(callable,
			     nArgBytes,
			     converters,
			     (DWORD)CallPythonObject,
			     stdcall);
}
#else /* ! MS_WIN32 */

typedef struct {
	ffi_closure cl; /* the C callable */
	ffi_cif cif;
	PyObject *converters;
	PyObject *callable;
	ffi_type *atypes[0];
} ffi_info;

static void closure_fcn(ffi_cif *cif,
			void *resp,
			void **args,
			void *userdata)
{
	ffi_info *p = userdata;
	int nArgs = PySequence_Length(p->converters);
	void **pArgs = alloca(sizeof(void *) * nArgs);
	int i;

	/* args is an array containing pointers to pointers to arguments, but
	   CallPythonObject expects an array containing pointers to arguments.
	*/
	for (i = 0; i < nArgs; ++i) {
		pArgs[i] = *(void ***)args[i];
	}

	/* Fixme: return type */
	*(int *)resp = CallPythonObject(p->callable,
					p->converters,
					pArgs);
}

THUNK AllocFunctionCallback(PyObject *callable,
			    int nArgBytes,
			    PyObject *converters,
			    int stdcall)
{
	int result;
	ffi_info *p;
	int nArgs, i;

	nArgs = PySequence_Size(converters);
	p = malloc(sizeof(ffi_info) + sizeof(ffi_type) * nArgs);

	/* Check for NULL */
	for (i = 0; i < nArgs; ++i) {
		p->atypes[i] = &ffi_type_sint;
	}

	/* XXX Check for FFI_OK */
	result = ffi_prep_cif(&p->cif, FFI_DEFAULT_ABI, nArgs,
			      &ffi_type_sint,
			      &p->atypes[0]);

	/* XXX Check for FFI_OK */
	result = ffi_prep_closure(&p->cl, &p->cif, closure_fcn, p);
	p->converters = converters;
	p->callable = callable;

	return (THUNK)p;
}
#endif /* MS_WIN32 */

void FreeCallback(THUNK thunk)
{
	free(thunk);
}

/****************************************************************************
 *
 * callback objects: initialization
 */

void init_callbacks_in_module(PyObject *m)
{
#ifdef MS_WIN32
	CALLBACKINFO (__stdcall *pFunc)(DWORD);
	pFunc = (CALLBACKINFO (__stdcall *)(DWORD)) CallbackTemplate;
	ti = pFunc(0);
#endif

	if (PyType_Ready((PyTypeObject *)&PyType_Type) < 0)
		return;

	g_interp = PyThreadState_Get()->interp;
}

#ifdef MS_WIN32
static void LoadPython(void)
{
	PyObject *mod;
	PyEval_InitThreads();
	Py_Initialize();
	mod = PyImport_ImportModule("ctcom.server");
	Py_XDECREF(mod);
}

long Call_GetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv)
{
	PyObject *mod, *func, *result;
	long retval;

	mod = PyImport_ImportModule("ctcom.server");
	if (!mod) {
		PyErr_Print();
		return E_FAIL;
	}

	func = PyObject_GetAttrString(mod, "DllGetClassObject");
	Py_DECREF(mod);
	if (!func) {
		PyErr_Print();
		return E_FAIL;
	}

	result = PyObject_CallFunction(func,
				       "iii", rclsid, riid, ppv);
	Py_DECREF(func);
	if (!result) {
		PyErr_Print();
		return E_FAIL;
	}

	retval = PyInt_AsLong(result);
	if (PyErr_Occurred())
		PyErr_Print();
	Py_DECREF(result);
	return retval;
}

STDAPI DllGetClassObject(REFCLSID rclsid,
			 REFIID riid,
			 LPVOID *ppv)
{
	long result;

	if (!Py_IsInitialized()) {
		LoadPython();
		LeavePython("Loaded");
	}
	EnterPython("DllGetClassObject");
	result = Call_GetClassObject(rclsid, riid, ppv);
	LeavePython("DllGetClassObject");
	return result;
}

long Call_CanUnloadNow(void)
{
	PyObject *mod, *func, *result;
	long retval;

	mod = PyImport_ImportModule("ctcom.server");
	if (!mod) {
		PyErr_Print();
		return E_FAIL;
	}

	func = PyObject_GetAttrString(mod, "DllCanUnloadNow");
	Py_DECREF(mod);
	if (!func) {
		PyErr_Print();
		return E_FAIL;
	}

	result = PyObject_CallFunction(func, NULL);
	Py_DECREF(func);
	if (!result) {
		PyErr_Print();
		return E_FAIL;
	}

	retval = PyInt_AsLong(result);
	if (PyErr_Occurred())
		PyErr_Print();
	Py_DECREF(result);
	{
		char buffer[64];
		sprintf(buffer, "_ctypes: DLLCANUNLOADNOW returns %d\n", retval);
		OutputDebugString(buffer);
	}
	return retval;
}

STDAPI DllCanUnloadNow(void)
{
	long result;

	if (!Py_IsInitialized()) {
		LoadPython();
		LeavePython("Loaded");
	}
	EnterPython("CanUnloadNow");
	result = Call_CanUnloadNow();
	LeavePython("CanUnloadNow");
	return result;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvRes)
{
	switch(fdwReason) {
	case DLL_PROCESS_ATTACH:
		DisableThreadLibraryCalls(hinstDLL);
		break;
	}
	return TRUE;
}
#endif

/*
 Local Variables:
 compile-command: "python setup.py build -g && python setup.py build install --home ~"
 End:
*/
