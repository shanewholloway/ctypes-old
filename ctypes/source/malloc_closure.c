/* Allocate executable memory */
#include <Python.h>
#include <ffi.h>
#include "ctypes.h"


#ifdef Py_DEBUG
#define MALLOC_CLOSURE_DEBUG
#endif

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

BLOCK *start;
unsigned int _pagesize;

#define BLOCKSIZE _pagesize * 4

static BLOCK *get_block(void)
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
	printf("One BLOCK has %d closures\n", block->count);

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
		for (i = 0; i < block->count; ++i) {
			if (&block->closure[i] == pcl) {
				block->closure[i].cif = NULL;
				--block->used;
				goto done;
			}
		}
		block = block->next;
	}
	Py_FatalError("ctypes: closure not found in heap");

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
			if (start)
				start->prev = NULL;
			else
				Py_FatalError("ctypes: no free block left\n");
		}

		/* now, block can be freed */
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
		block = start = get_block();

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
			BLOCK *new_block = get_block();
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
