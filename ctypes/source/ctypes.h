/******************************************************************/

#ifndef MS_WIN32
#define max(a, b) ((a) > (b) ? (a) : (b))
#define min(a, b) ((a) < (b) ? (a) : (b))
#endif

/*
  Backwards compatibility:
  Python2.2 used LONG_LONG instead of PY_LONG_LONG
*/
#if defined(HAVE_LONG_LONG) && !defined(PY_LONG_LONG)
#define PY_LONG_LONG LONG_LONG
#endif

typedef struct tagCDataObject CDataObject;
typedef int (*THUNK)(void);

/*
  Hm. Are there CDataObject's which do not need the b_objects member?  In
  this case we probably should introduce b_flags to mark it as present...  If
  b_objects is not present/unused b_length is unneeded as well.
*/

struct tagCDataObject {
	PyObject_HEAD
	char *b_ptr;		/* pointer to memory block */
	int  b_needsfree;	/* need _we_ free the memory? */
	CDataObject *b_base;	/* pointer to base object or NULL */
	int b_size;		/* size of memory block in bytes */
	int b_length;		/* number of references we need */
	int b_index;		/* index of this object into base's
				   b_object list */

	PyObject *b_objects;	/* list of references we need to keep */
};

typedef struct {
	/* First part identical to tagCDataObject */
	PyObject_HEAD
	char *b_ptr;		/* pointer to memory block */
	int  b_needsfree;	/* need _we_ free the memory? */
	CDataObject *b_base;	/* pointer to base object or NULL */
	int b_size;		/* size of memory block in bytes */
	int b_length;		/* number of references we need */
	int b_index;		/* index of this object into base's
				   b_object list */

	PyObject *b_objects;	/* list of references we need to keep */
	/* end of tagCDataObject, additional fields follow */

	THUNK thunk;
	PyObject *callable;

	/* These two fields will override the ones in the type's stgdict if
	   they are set */
	PyObject *converters;
	PyObject *argtypes;
	PyObject *restype;
#ifdef MS_WIN32
	int index;
#endif
} CFuncPtrObject;

extern PyObject *CData_GetList(CDataObject *mem);

extern PyTypeObject StgDict_Type;
#define StgDict_CheckExact(v)	    ((v)->ob_type == &StgDict_Type)
#define StgDict_Check(v)	    PyObject_TypeCheck(v, &StgDict_Type)
extern PyObject *StgDict_ForType(PyObject *type, int isStruct);
extern int PyType_stginfo(PyTypeObject *self, int *psize, int *palign, int *plength);
extern int PyObject_stginfo(PyObject *self, int *psize, int *palign, int *plength);



extern PyTypeObject CData_Type;
#define CDataObject_CheckExact(v)	((v)->ob_type == &CData_Type)
#define CDataObject_Check(v)		PyObject_TypeCheck(v, &CData_Type)

extern PyTypeObject SimpleType_Type;
#define SimpleTypeObject_CheckExact(v)	((v)->ob_type == &SimpleType_Type)
#define SimpleTypeObject_Check(v)	PyObject_TypeCheck(v, &SimpleType_Type)

extern PyTypeObject CField_Type;
extern struct fielddesc *getentry(char *fmt);


extern PyObject *
CField_FromDesc(PyObject *desc, int index,
		int *pfield_size, int bitsize, int *pbitofs,
		int *psize, int *poffset, int *palign, int pack);

extern PyObject *CData_AtAddress(PyObject *type, void *buf);
extern PyObject *CData_FromBytes(PyObject *type, char *data, int length);

extern PyTypeObject ArrayType_Type;
extern PyTypeObject Array_Type;
extern PyTypeObject PointerType_Type;
extern PyTypeObject Pointer_Type;
extern PyTypeObject CFuncPtr_Type;
extern PyTypeObject CFuncPtrType_Type;

#define ArrayTypeObject_Check(v)	PyObject_TypeCheck(v, &ArrayType_Type)
#define ArrayObject_Check(v)		PyObject_TypeCheck(v, &Array_Type)
#define PointerObject_Check(v)		PyObject_TypeCheck(v, &Pointer_Type)
#define PointerTypeObject_Check(v)	PyObject_TypeCheck(v, &PointerType_Type)
#define CFuncPtrObject_Check(v)		PyObject_TypeCheck(v, &CFuncPtr_Type)
#define CFuncPtrTypeObject_Check(v)	PyObject_TypeCheck(v, &CFuncPtrType_Type)

extern PyObject *
CreateArrayType(PyObject *itemtype, int length);

extern void init_callbacks_in_module(PyObject *m);

extern THUNK AllocFunctionCallback(PyObject *callable,
				   int nArgBytes,
				   PyObject *converters,
				   PyObject *restype,
				   int stdcall);
extern void FreeCallback(THUNK);

extern PyMethodDef module_methods[];

extern PyObject *sizeof_func(PyObject *self, PyObject *obj);
extern PyObject *align_func(PyObject *self, PyObject *obj);
extern PyObject *byref(PyObject *self, PyObject *obj);
extern PyObject *addressof(PyObject *self, PyObject *obj);

typedef PyObject *(* GETFUNC)(void *, unsigned size);
typedef PyObject *(* SETFUNC)(void *, PyObject *value, unsigned size);

/* a table entry describing a predefined ctypes type */
struct fielddesc {
	char code;
	SETFUNC setfunc;
	GETFUNC getfunc;
	ffi_type *pffi_type; /* always statically allocated */
};

typedef struct {
	PyObject_HEAD
	int offset;
	int size;
	int index;			/* Index into CDataObject's
					   object array */
	PyObject *proto;		/* a type or NULL */
	GETFUNC getfunc;		/* getter function if proto is NULL */
	SETFUNC setfunc;		/* setter function if proto is NULL */
} CFieldObject;

/* A subclass of PyDictObject, used as the instance dictionary of ctypes
   metatypes */
typedef struct {
	PyDictObject dict;	/* a subclass of dict */
	int size;		/* number of bytes */
	int align;		/* alignment requirements */
	int length;		/* number of fields */
	ffi_type ffi_type;
	PyObject *proto;	/* Only for Pointer/ArrayObject */
	SETFUNC setfunc;	/* Only for ArrayObject */
	GETFUNC getfunc;	/* Only for ArrayObject */

	/* Following fields only used by CFuncPtrType_Type instances */
	PyObject *argtypes;	/* tuple of CDataObjects */
	PyObject *converters;	/* tuple([t.from_param for t in argtypes]) */
	PyObject *restype;	/* CDataObject or NULL */
	int flags;		/* calling convention and such */
	int nArgBytes;		/* number of argument bytes for callback */
} StgDictObject;

/* May return NULL, but does not set an exception! */
extern StgDictObject *PyType_stgdict(PyObject *obj);

/* May return NULL, but does not set an exception! */
extern StgDictObject *PyObject_stgdict(PyObject *self);

typedef int(* PPROC)(void);

PyObject *_CallProc(PPROC pProc,
		    PyObject *arguments,
		    void *pIUnk,
		    int flags,
		    PyObject *argtypes,
		    PyObject *restype);

/*
 * TODO:
 * call_commethod is really slow.
 *
 *   It should also take an optional argtypes (hm, converters) argument.
 *   It should not be called with the (integer) this argument,
 *   instead it should retrieve the 'this' value itself - IOW, use
 *   the b_ptr contents directly.
 *
 * Change the signature of _CallProc into:
 *
PyObject *_CallProc(PPROC pProc,
		    PyObject *argtuple,
		    void *pIunk,
		    int flags,
		    PyObject *converters,
		    PyObject *restype);
 */
 

#define FUNCFLAG_STDCALL 0x0
#define FUNCFLAG_CDECL   0x1
#define FUNCFLAG_HRESULT 0x2
#define FUNCFLAG_PYTHONAPI 0x4

typedef struct {
	PyObject_HEAD
	ffi_type *pffi_type;
	char tag;
	union {
		char c;
		char b;
		short h;
		int i;
		long l;
#ifdef HAVE_LONG_LONG
		PY_LONG_LONG q;
#endif
		double d;
		float f;
		void *p;
	} value;
	PyObject *obj;
	int size; /* for the 'V' tag */
} PyCArgObject;

extern PyTypeObject PyCArg_Type;
extern PyCArgObject *new_CArgObject(void);
#define PyCArg_CheckExact(v)	    ((v)->ob_type == &PyCArg_Type)
extern PyCArgObject *new_CArgObject(void);

extern PyObject *
CData_get(PyObject *type, GETFUNC getfunc, PyObject *src,
	  int index, int size, char *ptr);

extern int
CData_set(PyObject *dst, PyObject *type, SETFUNC setfunc, PyObject *value,
	  int index, int size, char *ptr);

extern void Extend_Error_Info(PyObject *exc_class, char *fmt, ...);

struct basespec {
	CDataObject *base;
	int index;
	char *adr;
};

extern char basespec_string[];

extern ffi_type *GetType(PyObject *obj);

/* exception classes */
extern PyObject *PyExc_ArgError;

extern char *conversion_mode_encoding;
extern char *conversion_mode_errors;

/* Python 2.4 macros, which are not available in Python 2.3 */

#ifndef Py_CLEAR
#define Py_CLEAR(op)				\
        do {                            	\
                if (op) {			\
                        PyObject *tmp = (PyObject *)(op);	\
                        (op) = NULL;		\
                        Py_DECREF(tmp);		\
                }				\
        } while (0)
#endif

#ifndef Py_VISIT
/* Utility macro to help write tp_traverse functions.
 * To use this macro, the tp_traverse function must name its arguments
 * "visit" and "arg".  This is intended to keep tp_traverse functions
 * looking as much alike as possible.
 */
#define Py_VISIT(op)					\
        do { 						\
                if (op) {				\
                        int vret = visit((op), arg);	\
                        if (vret)			\
                                return vret;		\
                }					\
        } while (0)
#endif

/* Python's PyUnicode_*WideChar functions are broken ... */
#if defined(Py_USING_UNICODE) && defined(HAVE_WCHAR_H)
#  define CTYPES_UNICODE
#endif


#ifdef CTYPES_UNICODE
#  undef PyUnicode_FromWideChar
#  define PyUnicode_FromWideChar My_PyUnicode_FromWideChar

#  undef PyUnicode_AsWideChar
#  define PyUnicode_AsWideChar My_PyUnicode_AsWideChar

extern PyObject *My_PyUnicode_FromWideChar(const wchar_t *, int);
extern int My_PyUnicode_AsWideChar(PyUnicodeObject *, wchar_t *, int);

#endif

extern void FreeClosure(void *);
extern void *MallocClosure(void);

/*
 Local Variables:
 compile-command: "python setup.py -q build install --home ~"
 End:
*/
