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
#include <Python.h>
#include <ffi.h>
#include "ctypes.h"

/* BLOCKSIZE can be adjusted.  Larger blocksize will make MallocClosure() and
   FreeClosure() somewhat slower, but allocate less blocks from the system.
   It may be that some systems have a limit of how many mmap'd blocks can be
   open.

   sizeof(ffi_closure) typically is:

   Windows: 28 bytes
   Linux x86, OpenBSD x86: 24 bytes
   Linux x86_64: 48 bytes
*/

#define BLOCKSIZE _pagesize * 4

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

typedef struct _tagblock {
	struct _tagblock *next;
	struct _tagblock *prev;
	int count;
	int used;
	ffi_closure closure[0];
} BLOCK;

static BLOCK *start; /* points to the list of allocated blocks */
static unsigned int _pagesize; /* the system's pagesize */

static BLOCK *allocate_block(void)
{
	BLOCK *block;
#ifdef MS_WIN32
	if (!_pagesize) {
		SYSTEM_INFO systeminfo;
		GetSystemInfo(&systeminfo);
		_pagesize = systeminfo.dwPageSize;
	}

	block = (BLOCK *)VirtualAlloc(NULL,
				    BLOCKSIZE,
				    MEM_COMMIT,
				    PAGE_EXECUTE_READWRITE);
	if (block == NULL)
		return NULL;
#else
	if (!_pagesize) {
		_pagesize = sysconf(_SC_PAGESIZE);
	}
	block = (BLOCK *)mmap(NULL,
			    BLOCKSIZE,
			    PROT_READ | PROT_WRITE | PROT_EXEC,
			    MAP_PRIVATE | MAP_ANONYMOUS,
			    -1,
			    0);
	if (block == (void *)MAP_FAILED)
		return NULL;
	memset(block, 0, BLOCKSIZE);
#endif
	block->count = (BLOCKSIZE - sizeof(block)) / sizeof(ffi_closure);

#ifdef MALLOC_CLOSURE_DEBUG
	printf("One BLOCK has %d closures of %d bytes each\n",
	       block->count, sizeof(ffi_closure));
	block->count = 1;
	printf("ALLOCATED block %p\n", block);
#endif
	return block;
}

static void free_block(BLOCK *block)
{
#ifdef MS_WIN32
	if (0 == VirtualFree(block, 0, MEM_RELEASE))
		Py_FatalError("ctypes: executable memory head corrupted");
#else
	if (-1 == munmap((void *)block, BLOCKSIZE))
		Py_FatalError("ctypes: executable memory head corrupted");
#endif
}

/******************************************************************/

void FreeClosure(void *p)
{
	BLOCK *block = start;
	ffi_closure *pcl = (ffi_closure *)p;
	int i;

	while (block) {
		/* We could calculate the entry by pointer arithmetic,
		   to avoid a linear search.
		*/
		for (i = 0; i < block->count; ++i) {
			if (&block->closure[i] == pcl) {
				block->closure[i].cif = NULL;
				--block->used;
				goto done;
			}
		}
		block = block->next;
	}
	Py_FatalError("ctypes: closure not found in any block");

  done:
	if (block->used == 0) {
		if (block == start && block->next == NULL) {
			/* don't free the last block */
#ifdef MALLOC_CLOSURE_DEBUG
			printf("Don't free the very last block %p\n", block);
#endif
			return;
		}
		/* unlink the current block from the chain */
		if (block->next)
			block->next->prev = block->prev;
		if (block->prev) {
			block->prev->next = block->next;
		} else {
			start = block->next;
			start->prev = NULL;
		}

		/* now, the block can be freed */
		free_block(block);
#ifdef MALLOC_CLOSURE_DEBUG
		printf("FREEING block %p\n", block);
#endif
	}
}

void *MallocClosure(void)
{
	BLOCK *block = start;
	int i;

	if (start == NULL)
		block = start = allocate_block();

	while(block) {
		if (block->used < block->count) {
			/* This block has a free entry */
			for (i = 0; i < block->count; ++i) {
				if (block->closure[i].cif == NULL) {
					block->closure[i].cif = (ffi_cif *)-1;
					++block->used;
					return &block->closure[i];
				}
			}
			/* oops, where is it? */
			Py_FatalError("ctypes: use count on block is wrong");
		}
		if (block->next)
			/* try the next block, if there is one */
			block = block->next;
		else {
			/* need a fresh block */
			BLOCK *new_block = allocate_block();
			if (new_block == NULL)
				return NULL;
			/* insert into chain */
			new_block->prev = block;
			block->next = new_block;
			block = new_block;
		}
	}
	return NULL;
}
