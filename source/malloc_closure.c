/*
 * Memory blocks with executable permission are allocated of size BLOCKSIZE.
 * They are chained together, and the start of the chain is the global 'start'
 * pointer.
 *
 * Each block has an array of ffi_closure in it.  The ffi_closure.cif field is
 * used to mark an entry used or free, and the block has a 'used' field which
 * counts the used entries.
 *
 * MallocClosure() returns a pointer to an ffi_closure entry, allocating a new
 * block when needed.
 *
 * FreeClosure(ffi_closure*) marks the ffi_closure entry unused again.
 * If a memory block has only unused entries, it is freed again - unless it is
 * the last one in use.
 */

/*
 * The functions would probably be much faster if we would maintain a linked
 * list of free and used entries - this would avoid the linear searches.
 */

#include <Python.h>
#include <ffi.h>
#include "ctypes.h"

/* BLOCKSIZE can be adjusted.  Larger blocksize will take a larger memory
   overhead, but allocate less blocks from the system.  It may be that some
   systems have a limit of how many mmap'd blocks can be open.
*/

#define BLOCKSIZE _pagesize

/* #define MALLOC_CLOSURE_DEBUG */ /* enable for some debugging output */

/******************************************************************/

#ifdef MS_WIN32
#include <windows.h>
#else
#include <sys/mman.h>
#include <unistd.h>
# if !defined(MAP_ANONYMOUS) && defined(MAP_ANON)
#  define MAP_ANONYMOUS MAP_ANON
# endif
#endif

typedef struct _tagITEM {
	ffi_closure closure;
	struct _tagITEM *next;
} ITEM;

static ITEM *free_list;
int _pagesize;

static void more_core(void)
{
	ITEM *item;
	int count, i;

/* determine the pagesize */
#ifdef MS_WIN32
	if (!_pagesize) {
		SYSTEM_INFO systeminfo;
		GetSystemInfo(&systeminfo);
		_pagesize = systeminfo.dwPageSize;
	}
#else
	if (!_pagesize) {
		_pagesize = sysconf(_SC_PAGESIZE);
	}
#endif

	/* calculate the number of nodes to allocate */
	count = BLOCKSIZE / sizeof(ITEM);

	/* allocate a memory block */
#ifdef MS_WIN32
	item = (ITEM *)VirtualAlloc(NULL,
					       count * sizeof(ITEM),
					       MEM_COMMIT,
					       PAGE_EXECUTE_READWRITE);
	if (item == NULL)
		return;
#else
	item = (ITEM *)mmap(NULL,
			    count * sizeof(ITEM),
			    PROT_READ | PROT_WRITE | PROT_EXEC,
			    MAP_PRIVATE | MAP_ANONYMOUS,
			    -1,
			    0);
	if (item == (void *)MAP_FAILED)
		return;
#endif

#ifdef MALLOC_CLOSURE_DEBUG
	printf("block at %p allocated (%d bytes), %d ITEMs\n",
	       item, count * sizeof(ITEM), count);
#endif
	/* put them into the free list */
	for (i = 0; i < count; ++i) {
		item->next = free_list;
		free_list = item;
		++item;
	}
}

/******************************************************************/

/* put the item back into the free list */
void FreeClosure(void *p)
{
	ITEM *item = (ITEM *)p;
	item->next = free_list;
	free_list = item;
}

/* return one item from the free list, allocating more if needed */
void *MallocClosure(void)
{
	ITEM *item;
	if (!free_list)
		more_core();
	if (!free_list)
		return NULL;
	item = free_list;
	free_list = item->next;
	return item;
}
