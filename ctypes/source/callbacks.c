#include "Python.h"
#include <ffi.h>
#include "ctypes.h"

#ifdef MS_WIN32
#include <windows.h>
#define alloca _alloca
#endif

/* For 2.3, use the PyGILState_ calls, see PEP 311 */
#if (PY_VERSION_HEX >= 0x02030000)
#define CTYPES_USE_GILSTATE
#endif

#ifndef CTYPES_USE_GILSTATE
static PyInterpreterState *g_interp;	/* need this to create new thread states */

static void EnterPython(void)
{
	PyThreadState *pts;
	if (!g_interp)
		Py_FatalError("_ctypes: no interpreter state");
	PyEval_AcquireLock();
	pts = PyThreadState_New(g_interp);
	if (!pts)
		Py_FatalError("_ctypes: Could not allocate ThreadState");
	if (NULL != PyThreadState_Swap(pts))
		Py_FatalError("_ctypes (EnterPython): thread state not == NULL?");
}

static void LeavePython(void)
{
	PyThreadState *pts = PyThreadState_Get();
	if (!pts)
		Py_FatalError("_ctypes (LeavePython): ThreadState is NULL?");
	PyThreadState_Clear(pts);
	pts = PyThreadState_Swap(NULL);
	PyThreadState_Delete(pts);
	PyEval_ReleaseLock();
}
#endif

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

#ifdef MS_WIN32
/*
 * We must call AddRef() on non-NULL COM pointers we receive as arguments
 * to callback functions - these functions are COM method implementations.
 * The Python instances we create have a __del__ method which calls Release().
 *
 * The presence of a class attribute named '_needs_com_addref_' triggers this
 * behaviour.  It would also be possible to call the AddRef() Python method,
 * after checking for PyObject_IsTrue(), but this would probably be somewhat
 * slower.
 */
static void
TryAddRef(StgDictObject *dict, CDataObject *obj)
{
	IUnknown *punk;

	if (NULL == PyDict_GetItemString((PyObject *)dict, "_needs_com_addref_"))
		return;

	punk = *(IUnknown **)obj->b_ptr;
	if (punk)
		punk->lpVtbl->AddRef(punk);
	return;
}
#endif

/******************************************************************************
 *
 * Call the python object with all arguments
 *
 */
static void _CallPythonObject(void *mem,
			      ffi_type *restype,
			      SETFUNC setfunc,
			      PyObject *callable,
			      PyObject *converters,
			      void **pArgs)
{
	int i;
	PyObject *result;
	PyObject *arglist = NULL;
	int nArgs;

#ifdef CTYPES_USE_GILSTATE
	PyGILState_STATE state = PyGILState_Ensure();
#else
	EnterPython();
#endif

	nArgs = PySequence_Length(converters);
	/* Hm. What to return in case of error?
	   For COM, 0xFFFFFFFF seems better than 0.
	*/
	if (nArgs < 0) {
		PrintError("BUG: PySequence_Length");
		goto Done;
	}

	arglist = PyTuple_New(nArgs);
	if (!arglist) {
		PrintError("PyTuple_New()");
		goto Done;
	}
	for (i = 0; i < nArgs; ++i) {
		/* Note: new reference! */
		PyObject *cnv = PySequence_GetItem(converters, i);
		StgDictObject *dict;
		if (cnv)
			dict = PyType_stgdict(cnv);
		else {
			PrintError("Getting argument converter %d\n", i);
			goto Done;
		}

		if (dict && dict->getfunc) {
			PyObject *v = dict->getfunc(*pArgs, dict->size);
			if (!v) {
				PrintError("create argument %d:\n", i);
				goto Done;
			}
			PyTuple_SET_ITEM(arglist, i, v);
			/* XXX XXX XX
			   We have the problem that c_byte or c_short have dict->size of
			   1 resp. 4, but these parameters are pushed as sizeof(int) bytes.
			   BTW, the same problem occurrs when they are pushed as parameters
			*/
		} else if (dict) {
			/* Hm, shouldn't we use CData_AtAddress() or something like that instead? */
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
			memcpy(obj->b_ptr, *pArgs, dict->size);
			PyTuple_SET_ITEM(arglist, i, (PyObject *)obj);
#ifdef MS_WIN32
			TryAddRef(dict, obj);
#endif
		} else {
			PyErr_SetString(PyExc_TypeError,
					"cannot build parameter");
			PrintError("Parsing argument %d\n", i);
			goto Done;
		}
		/* XXX error handling! */
		pArgs++;
	}
	result = PyObject_CallObject(callable, arglist);
	if (!result) {
		Extend_Error_Info(PyExc_RuntimeError, "(in callback) ");
		PyErr_Print();
	} else if (result != Py_None) {
		/* another big endian hack */
		union {
			char c;
			short s;
			int i;
			long l;
		} r;
		PyObject *keep;
		switch (restype->size) {
		case 1:
			keep = setfunc(&r, result, 0);
			*(ffi_arg *)mem = r.c;
			break;
		case SIZEOF_SHORT:
			keep = setfunc(&r, result, 0);
			*(ffi_arg *)mem = r.s;
			break;
		case SIZEOF_INT:
			keep = setfunc(&r, result, 0);
			*(ffi_arg *)mem = r.i;
			break;
#if (SIZEOF_LONG != SIZEOF_INT)
		case SIZEOF_LONG:
			keep = setfunc(&r, result, 0);
			*(ffi_arg *)mem = r.l;
			break;
#endif
		default:
			keep = setfunc(mem, result, 0);
			break;
		}
		if (keep == NULL) {
			Extend_Error_Info(PyExc_RuntimeError, "(callback return type) ");
			PyErr_Print();
		} else {
			/* assert (keep == Py_None); */
			/* XXX We have no way to keep the needed reference XXX */
			/* Should we emit a warning? */
			Py_DECREF(keep);
		}
	}
	Py_XDECREF(result);
  Done:
	Py_XDECREF(arglist);
	
#ifdef CTYPES_USE_GILSTATE
	PyGILState_Release(state);
#else
	LeavePython();
#endif
}

typedef struct {
/*	ffi_closure cl; /* the C callable */
	ffi_closure *pcl; /* the C callable */
	ffi_cif cif;
	PyObject *converters;
	PyObject *callable;
	SETFUNC setfunc;
	ffi_type *restype;
	ffi_type *atypes[0];
} ffi_info;

static void closure_fcn(ffi_cif *cif,
			void *resp,
			void **args,
			void *userdata)
{
	ffi_info *p = userdata;

	_CallPythonObject(resp,
			  p->restype,
			  p->setfunc,
			  p->callable,
			  p->converters,
			  args);
}

void FreeCallback(THUNK thunk)
{
	FreeExecMem(*(void **)thunk);
	PyMem_Free(thunk);
}

THUNK AllocFunctionCallback(PyObject *callable,
			    int nArgBytes,
			    PyObject *converters,
			    PyObject *restype,
			    int is_cdecl)
{
	int result;
	ffi_info *p;
	int nArgs, i;
	ffi_abi cc;

	nArgs = PySequence_Size(converters);
	p = (ffi_info *)PyMem_Malloc(sizeof(ffi_info) + sizeof(ffi_type) * nArgs);
	if (p == NULL) {
		PyErr_NoMemory();
		return NULL;
	}
	p->pcl = MallocExecMem(sizeof(ffi_info));

	for (i = 0; i < nArgs; ++i) {
		PyObject *cnv = PySequence_GetItem(converters, i);
		p->atypes[i] = GetType(cnv);
		Py_DECREF(cnv);
	}
	p->atypes[i] = NULL;

	{
		StgDictObject *dict = PyType_stgdict(restype);
		if (dict) {
			p->setfunc = dict->setfunc;
			p->restype = &dict->ffi_type;
		} else {
			p->setfunc = getentry("i")->setfunc;
			p->restype = &ffi_type_sint;
		}
	}

	cc = FFI_DEFAULT_ABI;
#ifdef MS_WIN32
	if (is_cdecl == 0)
		cc = FFI_STDCALL;
#endif
	result = ffi_prep_cif(&p->cif, cc, nArgs,
			      GetType(restype),
			      &p->atypes[0]);
	if (result != FFI_OK) {
		PyErr_Format(PyExc_RuntimeError,
			     "ffi_prep_cif failed with %d", result);
		PyMem_Free(p);
		return NULL;
	}
	result = ffi_prep_closure(p->pcl, &p->cif, closure_fcn, p);
	if (result != FFI_OK) {
		PyErr_Format(PyExc_RuntimeError,
			     "ffi_prep_closure failed with %d", result);
		PyMem_Free(p);
		return NULL;
	}

	p->converters = converters;
	p->callable = callable;

	return (THUNK)p;
}

/****************************************************************************
 *
 * callback objects: initialization
 */

void init_callbacks_in_module(PyObject *m)
{
	if (PyType_Ready((PyTypeObject *)&PyType_Type) < 0)
		return;

#ifndef CTYPES_USE_GILSTATE
	g_interp = PyThreadState_Get()->interp;
#endif
}

#ifdef MS_WIN32
/*
   Modeled after a function from Mark Hammond.

   Obtains a string from a Python traceback.  This is the exact same string as
   "traceback.print_exception" would return.

   Result is a string which must be free'd using PyMem_Free()
*/
#define TRACEBACK_FETCH_ERROR(what) {errMsg = what; goto done;}

char *PyTraceback_AsString(void)
{
	char *errMsg = NULL; /* holds a local error message */
	char *result = NULL; /* a valid, allocated result. */
	PyObject *modStringIO = NULL;
	PyObject *modTB = NULL;
	PyObject *obStringIO = NULL;
	PyObject *obResult = NULL;

	PyObject *type, *value, *traceback;

	PyErr_Fetch(&type, &value, &traceback);
	PyErr_NormalizeException(&type, &value, &traceback);
	
	modStringIO = PyImport_ImportModule("cStringIO");
	if (modStringIO==NULL)
		TRACEBACK_FETCH_ERROR("cant import cStringIO\n");

	obStringIO = PyObject_CallMethod(modStringIO, "StringIO", NULL);

	/* Construct a cStringIO object */
	if (obStringIO==NULL)
		TRACEBACK_FETCH_ERROR("cStringIO.StringIO() failed\n");

	modTB = PyImport_ImportModule("traceback");
	if (modTB==NULL)
		TRACEBACK_FETCH_ERROR("cant import traceback\n");

	obResult = PyObject_CallMethod(modTB, "print_exception",
				       "OOOOO",
				       type, value ? value : Py_None,
				       traceback ? traceback : Py_None,
				       Py_None,
				       obStringIO);
				    
	if (obResult==NULL) 
		TRACEBACK_FETCH_ERROR("traceback.print_exception() failed\n");
	Py_DECREF(obResult);

	obResult = PyObject_CallMethod(obStringIO, "getvalue", NULL);
	if (obResult==NULL) 
		TRACEBACK_FETCH_ERROR("getvalue() failed.\n");

	/* And it should be a string all ready to go - duplicate it. */
	if (!PyString_Check(obResult))
			TRACEBACK_FETCH_ERROR("getvalue() did not return a string\n");

	{ // a temp scope so I can use temp locals.
		char *tempResult = PyString_AsString(obResult);
		result = (char *)PyMem_Malloc(strlen(tempResult)+1);
		if (result==NULL)
			TRACEBACK_FETCH_ERROR("memory error duplicating the traceback string\n");
		strcpy(result, tempResult);
	} // end of temp scope.
done:
	/* All finished - first see if we encountered an error */
	if (result==NULL && errMsg != NULL) {
		result = (char *)PyMem_Malloc(strlen(errMsg)+1);
		if (result != NULL)
			/* if it does, not much we can do! */
			strcpy(result, errMsg);
	}
	Py_XDECREF(modStringIO);
	Py_XDECREF(modTB);
	Py_XDECREF(obStringIO);
	Py_XDECREF(obResult);
	Py_XDECREF(value);
	Py_XDECREF(traceback);
	Py_XDECREF(type);
	return result;
}

void MyPyErr_Print(char *msg)
{
	char *text;

	text = PyTraceback_AsString();
	MessageBox(NULL,
		   text,
		   msg,
		   MB_OK | MB_ICONSTOP);
	PyMem_Free(text);
}

static void LoadPython(void)
{
	if (!Py_IsInitialized()) {
		PyEval_InitThreads();
		Py_Initialize();
	} else {
#ifndef CTYPES_USE_GILSTATE
		/* Python is already initialized.
		   We assume we don't have the lock.
		*/
		if (!g_interp) {
			g_interp = PyInterpreterState_Head();
			if(PyInterpreterState_Next(g_interp))
				Py_FatalError("_ctypes: more than one interpreter state");
		}
		EnterPython();
#endif
		return;
	}
}

/******************************************************************/

long Call_GetClassObject(REFCLSID rclsid, REFIID riid, LPVOID *ppv)
{
	PyObject *mod, *func, *result;
	long retval;

	mod = PyImport_ImportModule("ctypes.com.server");
	if (!mod)
		/* There has been a warning before about this already */
		return E_FAIL;

	func = PyObject_GetAttrString(mod, "DllGetClassObject");
	Py_DECREF(mod);
	if (!func) {
		MyPyErr_Print("DllGetClassObject");
		return E_FAIL;
	}

	result = PyObject_CallFunction(func,
				       "iii", rclsid, riid, ppv);
	Py_DECREF(func);
	if (!result) {
		MyPyErr_Print("Called DllGetClassObject");
		return E_FAIL;
	}

	retval = PyInt_AsLong(result);
	if (PyErr_Occurred())
		MyPyErr_Print("Convert result of DllGetClassObject to int");
	Py_DECREF(result);
	return retval;
}

STDAPI DllGetClassObject(REFCLSID rclsid,
			 REFIID riid,
			 LPVOID *ppv)
{
	long result;

#ifdef CTYPES_USE_GILSTATE
	PyGILState_STATE state;
	LoadPython();
	state = PyGILState_Ensure();
#else
	LoadPython(); /* calls EnterPython itself */
#endif
	result = Call_GetClassObject(rclsid, riid, ppv);

#ifdef CTYPES_USE_GILSTATE
	PyGILState_Release(state);
#else
	LeavePython();
#endif
	return result;
}

long Call_CanUnloadNow(void)
{
	PyObject *mod, *func, *result;
	long retval;

	mod = PyImport_ImportModule("ctypes.com.server");
	if (!mod) {
		MyPyErr_Print("Importing ctypes.com.server in Call_CanUnloadNow");
		return E_FAIL;
	}

	func = PyObject_GetAttrString(mod, "DllCanUnloadNow");
	Py_DECREF(mod);
	if (!func) {
		PyErr_Clear();
		return E_FAIL;
	}

	result = PyObject_CallFunction(func, NULL);
	Py_DECREF(func);
	if (!result) {
		PyErr_Clear();
		return E_FAIL;
	}

	retval = PyInt_AsLong(result);
	if (PyErr_Occurred())
		PyErr_Clear();
	Py_DECREF(result);
	return retval;
}

/*
  DllRegisterServer and DllUnregisterServer still missing
*/

STDAPI DllCanUnloadNow(void)
{
	long result;
#ifdef CTYPES_USE_GILSTATE
	PyGILState_STATE state = PyGILState_Ensure();
#else
	if (!Py_IsInitialized()) {
		LoadPython();
		LeavePython();
	}
	EnterPython();
#endif
	result = Call_CanUnloadNow();
#ifdef CTYPES_USE_GILSTATE
	PyGILState_Release(state);
#else
	LeavePython();
#endif
	return result;
}

#ifndef Py_NO_ENABLE_SHARED
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

#endif

/*
 Local Variables:
 compile-command: "cd .. && python setup.py -q build_ext"
 End:
*/