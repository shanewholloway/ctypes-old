/******************************************************************/

#ifndef MS_WIN32
#define max(a, b) ((a) > (b) ? (a) : (b))
#define min(a, b) ((a) < (b) ? (a) : (b))
#endif

typedef struct tagCDataObject CDataObject;

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

extern PyObject *CData_GetList(CDataObject *mem);

extern PyTypeObject StgDict_Type;
#define StgDict_CheckExact(v)	    ((v)->ob_type == &StgDict_Type)
#define StgDict_Check(v)	    PyObject_TypeCheck(v, &StgDict_Type)
extern PyObject *StgDict_FromDict(PyObject *fields, PyObject *typedict,
				  int isStruct, int pack);
extern int PyType_stginfo(PyTypeObject *self, int *psize, int *palign, int *plength);
extern int PyObject_stginfo(PyObject *self, int *psize, int *palign, int *plength);



extern PyTypeObject CData_Type;
#define CDataObject_CheckExact(v)	((v)->ob_type == &CData_Type)
#define CDataObject_Check(v)		PyObject_TypeCheck(v, &CData_Type)

extern PyTypeObject SimpleType_Type;
#define SimpleTypeObject_CheckExact(v)	((v)->ob_type == &SimpleType_Type)
#define SimpleTypeObject_Check(v)	PyObject_TypeCheck(v, &SimpleType_Type)

extern PyTypeObject CString_Type;
#define CString_CheckExact(v)		((v)->ob_type == &CString_Type)
#define CString_Check(v)		PyObject_TypeCheck(v, &CString_Type)

extern PyTypeObject CWString_Type;
#define CWString_CheckExact(v)		((v)->ob_type == &CWString_Type)
#define CWString_Check(v)		PyObject_TypeCheck(v, &CWString_Type)

extern PyTypeObject CFunctionType_Type;
extern PyTypeObject CFunction_Type;
#define CFunction_Check(v)		PyObject_TypeCheck(v, &CFunction_Type)

extern PyTypeObject CField_Type;
extern struct fielddesc *getentry(char *fmt);


extern PyObject *
CField_FromDesc(PyObject *desc, int index,
		int *psize, int *poffset, int *palign, int pack);



extern PyObject *
CData_FromBaseObj(PyObject *type, PyObject *base, int index, int baseofs);

extern PyObject *CData_AtAddress(PyObject *type, void *buf);
extern PyObject *CData_FromBytes(PyObject *type, char *data, int length);

extern PyTypeObject ArrayType_Type;
extern PyTypeObject Array_Type;
extern PyTypeObject PointerType_Type;
extern PyTypeObject Pointer_Type;

#define ArrayObject_Check(v)		PyObject_TypeCheck(v, &Array_Type)
#define PointerObject_Check(v)		PyObject_TypeCheck(v, &Pointer_Type)
#define PointerTypeObject_Check(v)	PyObject_TypeCheck(v, &PointerType_Type)

extern PyObject *
CreateArrayType(PyObject *itemtype, int length);

typedef int (*THUNK)(void);

typedef struct tagFunctionObject {
	PyObject_HEAD
	PyObject *callable;		/* python callable object */
	PyObject *converters;		/* sequence of converters */
	THUNK callback;			/* C function pointer */
} CFunctionObject;

extern PyTypeObject CFunction_Type;
#define CFunctionObject_CheckExact(v)	    ((v)->ob_type == &CFunction_Type)
#define CFunctionObject_Check(v)	    PyObject_TypeCheck(v, &CFunction_Type)

extern void init_callbacks_in_module(PyObject *m);

extern THUNK AllocFunctionCallback(PyObject *callable,
				   int nArgBytes,
				   PyObject *converters,
				   int stdcall);
extern void FreeCallback(THUNK);

extern PyMethodDef module_methods[];

extern PyObject *sizeof_func(PyObject *self, PyObject *obj);
extern PyObject *align_func(PyObject *self, PyObject *obj);
extern PyObject *byref(PyObject *self, PyObject *obj);
extern PyObject *addressof(PyObject *self, PyObject *obj);

typedef PyObject *(* GETFUNC)(void *, unsigned size);
typedef PyObject *(* SETFUNC)(void *, PyObject *value, unsigned size);

struct fielddesc {
    char code;
    int size;
    int align;
    SETFUNC setfunc;
    GETFUNC getfunc;
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

typedef struct {
	PyDictObject dict;	/* a subclass of dict */
	int size;		/* number of bytes */
	int align;		/* alignment requirements */
	int length;		/* number of fields */
	PyObject *proto;	/* Only for Pointer/ArrayObject */
	SETFUNC setfunc;	/* Only for ArrayObject */
	GETFUNC getfunc;	/* Only for ArrayObject */
	char fmt;		/* Only for SimpleObject */

	/* Following fields only used by CFuncPtrType_Type instances */
/*	PyObject *argtypes;	/* tuple of CDataObjects */
/*	PyObject *converters;	/* tuple( [t.from_param for t in argtypes */
/*	PyObject *restype;	/* CDataObject or NULL */
/*	int flags;		/* calling convention and such */
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
 

#define FUNCFLAG_CDECL 0x1
#define FUNCFLAG_HRESULT 0x2

typedef struct {
	PyObject_HEAD
	char tag;
	union {
		char c;
		char b;
		short h;
		int i;
		long l;
#ifdef HAVE_LONG_LONG
		LONG_LONG q;
#endif
		double d;
		float f;
		void *p;
	} value;
	PyObject *obj;
} PyCArgObject;

extern PyTypeObject PyCArg_Type;
extern PyCArgObject *new_CArgObject(void);
#define PyCArg_CheckExact(v)	    ((v)->ob_type == &PyCArg_Type)
extern PyCArgObject *new_CArgObject(void);

extern PyObject *ToPython(void *, char tag);

/*
 Local Variables:
 compile-command: "python setup.py -q build install --home ~"
 End:
*/
