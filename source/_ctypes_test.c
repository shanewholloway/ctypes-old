#include <Python.h>

/*
  Backwards compatibility:
  Python2.2 used LONG_LONG instead of PY_LONG_LONG
*/
#if defined(HAVE_LONG_LONG) && !defined(PY_LONG_LONG)
#define PY_LONG_LONG LONG_LONG
#endif

#ifdef MS_WIN32
#include <windows.h>
#endif

#if defined(MS_WIN32) || defined(__CYGWIN__)
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

EXPORT(char *) my_strdup(char *src)
{
	char *dst = malloc(strlen(src)+1);
	if (!dst)
		return NULL;
	strcpy(dst, src);
	return dst;
}

#ifdef HAVE_WCHAR_H
EXPORT(wchar_t *) my_wcsdup(wchar_t *src)
{
	int len = wcslen(src);
	wchar_t *ptr = malloc((len + 1) * sizeof(wchar_t));
	if (ptr == NULL)
		return NULL;
	memcpy(ptr, src, (len+1) * sizeof(wchar_t));
	return ptr;
}

EXPORT(size_t) my_wcslen(wchar_t *src)
{
	return wcslen(src);
}
#endif

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

EXPORT(PY_LONG_LONG) _testfunc_callback_q_qf(PY_LONG_LONG value,
					     PY_LONG_LONG (*func)(PY_LONG_LONG))
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

typedef struct tagpoint {
	int x;
	int y;
} point;

EXPORT(int) _testfunc_byval(point in, point *pout)
{
	if (pout) {
		pout->x = in.x;
		pout->y = in.y;
	}
	return in.x + in.y;
}

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

EXPORT(PY_LONG_LONG) last_tf_arg_s;
EXPORT(unsigned PY_LONG_LONG) last_tf_arg_u;

struct BITS {
	int A: 1, B:2, C:3, D:4, E: 5, F: 6, G: 7, H: 8, I: 9;
	short M: 1, N: 2, O: 3, P: 4, Q: 5, R: 6, S: 7;
};

DL_EXPORT(void) set_bitfields(struct BITS *bits, char name, int value)
{
	switch (name) {
	case 'A': bits->A = value; break;
	case 'B': bits->B = value; break;
	case 'C': bits->C = value; break;
	case 'D': bits->D = value; break;
	case 'E': bits->E = value; break;
	case 'F': bits->F = value; break;
	case 'G': bits->G = value; break;
	case 'H': bits->H = value; break;
	case 'I': bits->I = value; break;

	case 'M': bits->M = value; break;
	case 'N': bits->N = value; break;
	case 'O': bits->O = value; break;
	case 'P': bits->P = value; break;
	case 'Q': bits->Q = value; break;
	case 'R': bits->R = value; break;
	case 'S': bits->S = value; break;
	}
}

DL_EXPORT(int) unpack_bitfields(struct BITS *bits, char name)
{
	switch (name) {
	case 'A': return bits->A;
	case 'B': return bits->B;
	case 'C': return bits->C;
	case 'D': return bits->D;
	case 'E': return bits->E;
	case 'F': return bits->F;
	case 'G': return bits->G;
	case 'H': return bits->H;
	case 'I': return bits->I;

	case 'M': return bits->M;
	case 'N': return bits->N;
	case 'O': return bits->O;
	case 'P': return bits->P;
	case 'Q': return bits->Q;
	case 'R': return bits->R;
	case 'S': return bits->S;
	}
	return 0;
}

PyMethodDef module_methods[] = {
//	{"get_last_tf_arg_s", get_last_tf_arg_s, METH_NOARGS},
//	{"get_last_tf_arg_u", get_last_tf_arg_u, METH_NOARGS},
	{"func_si", py_func_si, METH_VARARGS},
	{"func", py_func, METH_NOARGS},
	{ NULL, NULL, 0, NULL},
};

#define S last_tf_arg_s = (PY_LONG_LONG)c
#define U last_tf_arg_u = (unsigned PY_LONG_LONG)c

EXPORT(char) tf_b(char c) { S; return c/3; }
EXPORT(unsigned char) tf_B(unsigned char c) { U; return c/3; }
EXPORT(short) tf_h(short c) { S; return c/3; }
EXPORT(unsigned short) tf_H(unsigned short c) { U; return c/3; }
EXPORT(int) tf_i(int c) { S; return c/3; }
EXPORT(unsigned int) tf_I(unsigned int c) { U; return c/3; }
EXPORT(long) tf_l(long c) { S; return c/3; }
EXPORT(unsigned long) tf_L(unsigned long c) { U; return c/3; }
EXPORT(PY_LONG_LONG) tf_q(PY_LONG_LONG c) { S; return c/3; }
EXPORT(unsigned PY_LONG_LONG) tf_Q(unsigned PY_LONG_LONG c) { U; return c/3; }
EXPORT(float) tf_f(float c) { S; return c/3; }
EXPORT(double) tf_d(double c) { S; return c/3; }

#ifdef MS_WIN32
EXPORT(char) __stdcall s_tf_b(char c) { S; return c/3; }
EXPORT(unsigned char) __stdcall s_tf_B(unsigned char c) { U; return c/3; }
EXPORT(short) __stdcall s_tf_h(short c) { S; return c/3; }
EXPORT(unsigned short) __stdcall s_tf_H(unsigned short c) { U; return c/3; }
EXPORT(int) __stdcall s_tf_i(int c) { S; return c/3; }
EXPORT(unsigned int) __stdcall s_tf_I(unsigned int c) { U; return c/3; }
EXPORT(long) __stdcall s_tf_l(long c) { S; return c/3; }
EXPORT(unsigned long) __stdcall s_tf_L(unsigned long c) { U; return c/3; }
EXPORT(PY_LONG_LONG) __stdcall s_tf_q(PY_LONG_LONG c) { S; return c/3; }
EXPORT(unsigned PY_LONG_LONG) __stdcall s_tf_Q(unsigned PY_LONG_LONG c) { U; return c/3; }
EXPORT(float) __stdcall s_tf_f(float c) { S; return c/3; }
EXPORT(double) __stdcall s_tf_d(double c) { S; return c/3; }
#endif
/*******/

EXPORT(char) tf_bb(char x, char c) { S; return c/3; }
EXPORT(unsigned char) tf_bB(char x, unsigned char c) { U; return c/3; }
EXPORT(short) tf_bh(char x, short c) { S; return c/3; }
EXPORT(unsigned short) tf_bH(char x, unsigned short c) { U; return c/3; }
EXPORT(int) tf_bi(char x, int c) { S; return c/3; }
EXPORT(unsigned int) tf_bI(char x, unsigned int c) { U; return c/3; }
EXPORT(long) tf_bl(char x, long c) { S; return c/3; }
EXPORT(unsigned long) tf_bL(char x, unsigned long c) { U; return c/3; }
EXPORT(PY_LONG_LONG) tf_bq(char x, PY_LONG_LONG c) { S; return c/3; }
EXPORT(unsigned PY_LONG_LONG) tf_bQ(char x, unsigned PY_LONG_LONG c) { U; return c/3; }
EXPORT(float) tf_bf(char x, float c) { S; return c/3; }
EXPORT(double) tf_bd(char x, double c) { S; return c/3; }
EXPORT(void) tv_i(int c) { S; return; }

#ifdef MS_WIN32
EXPORT(char) __stdcall s_tf_bb(char x, char c) { S; return c/3; }
EXPORT(unsigned char) __stdcall s_tf_bB(char x, unsigned char c) { U; return c/3; }
EXPORT(short) __stdcall s_tf_bh(char x, short c) { S; return c/3; }
EXPORT(unsigned short) __stdcall s_tf_bH(char x, unsigned short c) { U; return c/3; }
EXPORT(int) __stdcall s_tf_bi(char x, int c) { S; return c/3; }
EXPORT(unsigned int) __stdcall s_tf_bI(char x, unsigned int c) { U; return c/3; }
EXPORT(long) __stdcall s_tf_bl(char x, long c) { S; return c/3; }
EXPORT(unsigned long) __stdcall s_tf_bL(char x, unsigned long c) { U; return c/3; }
EXPORT(PY_LONG_LONG) __stdcall s_tf_bq(char x, PY_LONG_LONG c) { S; return c/3; }
EXPORT(unsigned PY_LONG_LONG) __stdcall s_tf_bQ(char x, unsigned PY_LONG_LONG c) { U; return c/3; }
EXPORT(float) __stdcall s_tf_bf(char x, float c) { S; return c/3; }
EXPORT(double) __stdcall s_tf_bd(char x, double c) { S; return c/3; }
EXPORT(void) __stdcall s_tv_i(int c) { S; return; }
#endif

/********/
 
#ifndef MS_WIN32

typedef struct {
	long x;
	long y;
} POINT;

typedef struct {
	long left;
	long top;
	long right;
	long bottom;
} RECT;

typedef int HWND;
	
#endif

EXPORT(int) PointInRect(RECT *prc, POINT pt)
{
	if (pt.x < prc->left)
		return 0;
	if (pt.x > prc->right)
		return 0;
	if (pt.y < prc->top)
		return 0;
	if (pt.y > prc->bottom)
		return 0;
	return 1;
}

typedef struct {
	short x;
	short y;
} S2H;

EXPORT(S2H) ret_2h_func(S2H inp)
{
	inp.x *= 2;
	inp.y *= 3;
	return inp;
}

typedef struct {
	int a, b, c, d, e, f, g, h;
} S8I;

EXPORT(S8I) ret_8i_func(S8I inp)
{
	inp.a *= 2;
	inp.b *= 3;
	inp.c *= 4;
	inp.d *= 5;
	inp.e *= 6;
	inp.f *= 7;
	inp.g *= 8;
	inp.h *= 9;
	return inp;
}

EXPORT(HWND) my_GetDesktopWindow(void)
{
#ifdef MS_WIN32
	return GetDesktopWindow();
#else
	return 42;
#endif
}

EXPORT(int) my_GetWindowRect(HWND hwnd, RECT *prect)
{
#ifdef MS_WIN32
	return GetWindowRect(hwnd, prect);
#else
	return hwnd != 0;
#endif
}

EXPORT(void) TwoOutArgs(int a, int *pi, int b, int *pj)
{
	*pi += a;
	*pj += b;
}

#ifdef MS_WIN32
EXPORT(S2H) __stdcall s_ret_2h_func(S2H inp) { return ret_2h_func(inp); }
EXPORT(S8I) __stdcall s_ret_8i_func(S8I inp) { return ret_8i_func(inp); }
#endif

DL_EXPORT(void)
init_ctypes_test(void)
{
	Py_InitModule("_ctypes_test", module_methods);
}
