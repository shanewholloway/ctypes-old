#include <Python.h>
#include "ctypes.h"

#ifdef MS_WIN32
#include <windows.h>
#endif

/* Although this is compiled as a Python extension module, it's not really
   one.  But this is the easiest way to create a shared library.

   This library exports functions for testing _ctypes.
*/

PyObject *my_debug(PyObject *self, CDataObject *arg)
{
#ifdef MS_WIN32
  	DISPPARAMS *dp;
  	VARIANT *va;
 	OLECHAR FAR * FAR *p;
	FUNCDESC *f = (FUNCDESC *)(arg->b_ptr);

	ELEMDESC *pelemdesc = *(ELEMDESC **)arg->b_ptr;
 	int *pi;
 	char *cp;
 	char **cpp;
	IUnknown *pIunk = *(IUnknown **)(arg->b_ptr);
	IDispatch *pIDisp = (IDispatch *)(arg->b_ptr);
 	dp = (DISPPARAMS *)arg->b_ptr;
 	va = (VARIANT *)arg->b_ptr;
 	p = (OLECHAR FAR * FAR *)arg->b_ptr;
 	pi = (int *)arg->b_ptr;
 	cp = arg->b_ptr;
 	cpp = (char **)arg->b_ptr;
#ifdef _DEBUG
	_asm int 3;
/*
	Py_BEGIN_ALLOW_THREADS
	x = pIunk->lpVtbl->AddRef(pIunk);
	x = pIunk->lpVtbl->Release(pIunk);
	Py_END_ALLOW_THREADS
*/
#endif
#endif
	Py_INCREF(Py_None);
	return Py_None;
}


#ifdef MS_WIN32
#define EXPORT(x) __declspec(dllexport) x
#else
#define EXPORT(x) x
#endif

/* some functions handy for testing */

EXPORT(void) _testfunc_v(int a, int b, int *presult)
{
	*presult = a + b;
}

EXPORT(int) _testfunc_i_bhilfd(char b, short h, int i, long l, float f, double d)
{
//	printf("_testfunc_i_bhilfd got %d %d %d %ld %f %f\n",
//	       b, h, i, l, f, d);
	return (int)(b + h + i + l + f + d);
}

EXPORT(float) _testfunc_f_bhilfd(char b, short h, int i, long l, float f, double d)
{
//	printf("_testfunc_f_bhilfd got %d %d %d %ld %f %f\n",
//	       b, h, i, l, f, d);
	return (float)(b + h + i + l + f + d);
}

EXPORT(double) _testfunc_d_bhilfd(char b, short h, int i, long l, float f, double d)
{
//	printf("_testfunc_d_bhilfd got %d %d %d %ld %f %f\n",
//	       b, h, i, l, f, d);
	return (double)(b + h + i + l + f + d);
}

EXPORT(char *) _testfunc_p_p(void *s)
{
	return s;
}


EXPORT(void *) get_strchr(void)
{
	return (void *)strchr;
}


#ifndef MS_WIN32
# ifndef __stdcall
#  define __stdcall /* */
# endif
#endif

typedef struct {
	int (*c)(int, int);
	int (__stdcall *s)(int, int);
} FUNCS;

EXPORT(int) _testfunc_callfuncp(FUNCS *fp)
{
	fp->c(1, 2);
	fp->s(3, 4);
	return 0;
}

EXPORT(int) _testfunc_deref_pointer(int *pi)
{
	return *pi;
}

#ifdef MS_WIN32
EXPORT(int) _testfunc_piunk(IUnknown FAR *piunk)
{
	piunk->lpVtbl->AddRef(piunk);
	return piunk->lpVtbl->Release(piunk);
}
#endif

EXPORT(int) _testfunc_callback_with_pointer(int (*func)(int *))
{
	int table[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10};

	return (*func)(table);
}

#ifdef HAVE_LONG_LONG
EXPORT(PY_LONG_LONG) _testfunc_q_bhilfdq(char b, short h, int i, long l, float f,
				     double d, PY_LONG_LONG q)
{
	return (PY_LONG_LONG)(b + h + i + l + f + d + q);
}

EXPORT(PY_LONG_LONG) _testfunc_q_bhilfd(char b, short h, int i, long l, float f, double d)
{
	return (PY_LONG_LONG)(b + h + i + l + f + d);
}

EXPORT(int) _testfunc_callback_i_if(int value, int (*func)(int))
{
	int sum = 0;
	while (value != 0) {
		sum += func(value);
		value /= 2;
	}
	return sum;
}

EXPORT(int) _testfunc_callback_i_iif(int value, int (*func)(int, int))
{
	int sum = 0;
	while (value != 0) {
		sum += func(value, value*2);
		value /= 2;
	}
	if (sum == 0)
		_asm ret 8 ; a comment
	return sum;
}

EXPORT(int) _testfunc_stdcall_callback_i_iif(int value, int (__stdcall *func)(int, int))
{
	int sum = 0;
	while (value != 0) {
		sum += func(value, value*2);
		value /= 2;
	}
	return sum;
}

EXPORT(PY_LONG_LONG) _testfunc_callback_q_qf(PY_LONG_LONG value, int (*func)(PY_LONG_LONG))
{
	PY_LONG_LONG sum = 0;

	while (value != 0) {
		sum += func(value);
		value /= 2;
	}
	return sum;
}

#endif

EXPORT(int) _testfunc_ppp(char ***p)
{
	static char message[] = "Hello, World";
	if (p) {
		*p = malloc(sizeof(char *));
		printf("malloc returned %d\n", (int)*p);
		**p = message;
		return 1;
	}
	return 0;
}

EXPORT(void) my_free(void *p)
{
	printf("my_free got %d\n", (int)p);
}

typedef struct {
	char *name;
	char *value;
} SPAM;

typedef struct {
	char *name;
	int num_spams;
	SPAM *spams;
} EGG;

SPAM my_spams[2] = {
	{ "name1", "value1" },
	{ "name2", "value2" },
};

EGG my_eggs[1] = {
	{ "first egg", 1, my_spams }
};

EXPORT(int) getSPAMANDEGGS(EGG **eggs)
{
	*eggs = my_eggs;
	return 1;
}

#ifdef CAN_PASS_BY_VALUE
typedef struct tagpoint {
	int x;
	int y;
} point;

EXPORT(int) _testfunc_byval(point in, point *pout)
{
	static point buf;
	if (pout) {
		pout->x = in.x;
		pout->y = in.y;
	}
	return in.x + in.y;
}

#endif

EXPORT (int) an_integer = 42;

EXPORT(int) get_an_integer(void)
{
	return an_integer;
}

EXPORT(double)
integrate(double a, double b, double (*f)(double), long nstep)
{
	double x, sum=0.0, dx=(b-a)/(double)nstep;
	for(x=a+0.5*dx; (b-x)*(x-a)>0.0; x+=dx)
		sum += f(x);
	return sum/(double)nstep;
}

typedef struct {
	void (*initialize)(void *(*)(int), void(*)(void *));
} xxx_library;

static void _xxx_init(void *(*Xalloc)(int), void (*Xfree)(void *))
{
	void *ptr;
	
	printf("_xxx_init got %x %x\n", (int)Xalloc, (int)Xfree);
	printf("calling\n");
	ptr = Xalloc(32);
	Xfree(ptr);
	printf("calls done, ptr was %x\n", (int)ptr);
}

xxx_library _xxx_lib = {
	_xxx_init
};

EXPORT(xxx_library) *library_get(void)
{
	return &_xxx_lib;
}

#ifdef MS_WIN32
/* See Don Box (german), pp 79ff. */
EXPORT(void) GetString(BSTR *pbstr)
{
	*pbstr = SysAllocString(L"Goodbye!");
}
#endif

/*
 * Some do-nothing functions, for speed tests
 */
PyObject *py_func_si(PyObject *self, PyObject *args)
{
	char *name;
	int i;
	if (!PyArg_ParseTuple(args, "si", &name, &i))
		return NULL;
	Py_INCREF(Py_None);
	return Py_None;
}

EXPORT(void) _py_func_si(char *s, int i)
{
}

PyObject *py_func(PyObject *self, PyObject *args)
{
	Py_INCREF(Py_None);
	return Py_None;
}

EXPORT(void) _py_func(void)
{
}

PyMethodDef module_methods[] = {
	{"func_si", py_func_si, METH_VARARGS},
	{"func", py_func, METH_NOARGS},
#ifdef _DEBUG
	{"my_debug", my_debug, METH_O},
#endif
	{ NULL, NULL, 0, NULL},
};

DL_EXPORT(void)
init_ctypes_test(void)
{
	Py_InitModule("_ctypes_test", module_methods);
}
