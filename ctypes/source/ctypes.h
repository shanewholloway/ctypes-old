/******************************************************************/

#ifndef MS_WIN32
#define max(a, b) ((a) > (b) ? (a) : (b))
#define min(a, b) ((a) < (b) ? (a) : (b))

#define PARAMFLAG_FIN 1
#define PARAMFLAG_FOUT 2
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
	PyObject *checker;
#ifdef MS_WIN32
	int index;
#endif
	PyObject *paramflags;
} CFuncPtrObject;

extern PyTypeObject StgDict_Type;
#define StgDict_CheckExact(v)	    ((v)->ob_type == &StgDict_Type)
#define StgDict_Check(v)	    PyObject_TypeCheck(v, &StgDict_Type)

extern int StructUnionType_update_stgdict(PyObject *fields, PyObject *type, int isStruct);
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

extern PyTypeObject ArrayType_Type;
extern PyTypeObject Array_Type;
extern PyTypeObject PointerType_Type;
extern PyTypeObject Pointer_Type;
extern PyTypeObject CFuncPtr_Type;
extern PyTypeObject CFuncPtrType_Type;
extern PyTypeObject StructType_Type;

#define ArrayTypeObject_Check(v)	PyObject_TypeCheck(v, &ArrayType_Type)
#define ArrayObject_Check(v)		PyObject_TypeCheck(v, &Array_Type)
#define PointerObject_Check(v)		PyObject_TypeCheck(v, &Pointer_Type)
#define PointerTypeObject_Check(v)	PyObject_TypeCheck(v, &PointerType_Type)
#define CFuncPtrObject_Check(v)		PyObject_TypeCheck(v, &CFuncPtr_Type)
#define CFuncPtrTypeObject_Check(v)	PyObject_TypeCheck(v, &CFuncPtrType_Type)
#define StructTypeObject_Check(v)	PyObject_TypeCheck(v, &StructType_Type)

extern PyObject *
CreateArrayType(PyObject *itemtype, int length);

extern void init_callbacks_in_module(PyObject *m);

extern THUNK AllocFunctionCallback(PyObject *callable,
				   PyObject *converters,
				   PyObject *restype,
				   int stdcall);
extern void FreeCallback(THUNK);

extern PyMethodDef module_methods[];

typedef PyObject *(* GETFUNC)(void *ptr, unsigned size, PyObject *type, CDataObject *src, int index);
typedef PyObject *(* SETFUNC)(void *ptr, PyObject* value, unsigned size, PyObject *type);

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
	int size;			/* for bitfields, contains bitoffset and bitcount */
					
	int index;			/* Index into CDataObject's
					   object array */
	PyObject *fieldtype;		/* ctypes type of field */
	SETFUNC setfunc;		/* setter function if proto is NULL */
} CFieldObject;

/* A subclass of PyDictObject, used as the instance dictionary of ctypes
   metatypes */
typedef struct {
	PyDictObject dict;	/* first part identical to PyDictObject */
/* The size and align fields are unneeded, they are in ffi_type as well.  As
   an experiment shows, it's trivial to get rid of them, the only thing to
   remember is that in ArrayType_new the ffi_type fields must be filled in -
   so far it was unneeded because libffi doesn't support arrays at all
   (because they are passed as pointers to function calls anyway).  But it's
   too much risk to change that now, and there are other fields which doen't
   belong into this structure anyway.  Maybe in ctypes 2.0... (ctypes 2000?)
*/
	int size;		/* number of bytes */
	int align;		/* alignment requirements */
	int length;		/* number of fields */
	ffi_type ffi_type;
	PyObject *proto;	/* Only for Pointer/ArrayObject */
	SETFUNC setfunc;
	GETFUNC getfunc;

	/* Following fields only used by CFuncPtrType_Type instances */
	PyObject *argtypes;	/* tuple of CDataObjects */
	PyObject *converters;	/* tuple([t.from_param for t in argtypes]) */
	PyObject *restype;	/* CDataObject or NULL */
	PyObject *checker;
	int flags;		/* calling convention and such */
} StgDictObject;

/****************************************************************
 XXX No longer correct - update this when finished.

 StgDictObject fields

 setfunc and getfunc is only set for simple data types, it is copied from the
 corresponding fielddesc entry.  These are functions to set and get the value
 in a memory block.
 They should probably by used by other types as well.

 proto is only used for Pointer and Array types - it points to the item type
 object.

 Probably all the magic ctypes methods (like from_param) should have C
 callable wrappers in the StgDictObject.  For simple data type, for example,
 the fielddesc table could have entries for C codec from_param functions or
 other methods as well, if a subtype overrides this method in Python at
 construction time, or assigns to it later, tp_setattro should update the
 StgDictObject function to a generic one.

 Currently, CFuncPtr types have 'converters' and 'checker' entries in their
 type dict.  They are only used to cache attributes from other entries, whihc
 is wrong.

 One use case is the .value attribute that all simple types have.  But some
 complex structures, like VARIANT, represent a single value also, and should
 have this attribute.

 Another use case is a _check_retval_ function, which is called when a ctypes
 type is used as return type of a function to validate and compute the return
 value.

 Common ctypes protocol:

  - setfunc: store a python value in a memory block
  - getfunc: convert data from a memory block into a python value

  - checkfunc: validate and convert a return value from a function call
  - toparamfunc: convert a python value into a function argument

*****************************************************************/

/* May return NULL, but does not set an exception! */
extern StgDictObject *PyType_stgdict(PyObject *obj);

/* May return NULL, but does not set an exception! */
extern StgDictObject *PyObject_stgdict(PyObject *self);

extern int StgDict_clone(StgDictObject *src, StgDictObject *dst);

typedef int(* PPROC)(void);

extern PyObject *_CallProc(PPROC pProc,
			   PyObject *arguments,
			   void *pIUnk,
			   int flags,
			   PyObject *argtypes,
			   PyObject *restype,
			   PyObject *checker);
 
extern PyObject *CData_FromBaseObj(PyObject *type, PyObject *base,
				   int index, char *adr);

extern int KeepRef(CDataObject *target, int index, PyObject *keep);

extern PyObject *GetKeepedObjects(CDataObject *target);


#define FUNCFLAG_STDCALL 0x0
#define FUNCFLAG_CDECL   0x1
#define FUNCFLAG_HRESULT 0x2
#define FUNCFLAG_PYTHONAPI 0x4

#define DICTFLAG_FINAL 0x1000

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

extern void _AddTraceback(char *, char *, int);

/*
 Local Variables:
 compile-command: "python setup.py -q build install --home ~"
 End:
*/
