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

typedef struct _tagpage {
	struct _tagpage *next;
	struct _tagpage *prev;
	int count;
	int used;
	ffi_closure closure[0];
} PAGE;

PAGE *start;
unsigned int _pagesize;

#define BLOCKSIZE _pagesize * 4

static PAGE *get_page()
{
	PAGE *page;
#ifdef MS_WIN32
	if (!_pagesize) {
		SYSTEM_INFO systeminfo;
		GetSystemInfo(&systeminfo);
		_pagesize = systeminfo.dwPageSize;
	}

	page = (PAGE *)VirtualAlloc(NULL,
				    BLOCKSIZE,
				    MEM_COMMIT,
				    PAGE_EXECUTE_READWRITE);
	if (page == NULL)
		return NULL;
#else
	if (!_pagesize) {
		_pagesize = sysconf(_SC_PAGESIZE);
	}
	page = (PAGE *)mmap(NULL,
			    BLOCKSIZE,
			    PROT_READ | PROT_WRITE | PROT_EXEC,
			    MAP_PRIVATE | MAP_ANONYMOUS,
			    -1,
			    0);
	if (page == (void *)MAP_FAILED)
		return NULL;
	memset(page, 0, BLOCKSIZE);
#endif
	page->count = (BLOCKSIZE - sizeof(page)) / sizeof(ffi_closure);

#ifdef MALLOC_CLOSURE_DEBUG
	printf("One BLOCK has %d closures\n", page->count);

	page->count = 1;

	printf("ALLOCATED page %p\n", page);
#endif
	return page;
}

static void free_page(PAGE *page)
{
#ifdef MS_WIN32
	if (0 == VirtualFree(page, 0, MEM_RELEASE))
		Py_FatalError("ctypes: executable memory head corrupted");
#else
	if (-1 == munmap((void *)page, BLOCKSIZE))
		Py_FatalError("ctypes: executable memory head corrupted");
#endif
}

/******************************************************************/

void FreeClosure(void *p)
{
	PAGE *page = start;
	ffi_closure *pcl = (ffi_closure *)p;
	int i;

	while (page) {
		for (i = 0; i < page->count; ++i) {
			if (&page->closure[i] == pcl) {
				page->closure[i].cif = NULL;
				--page->used;
				goto done;
			}
		}
		page = page->next;
	}
	Py_FatalError("ctypes: closure not found in heap");

  done:
	if (page->used == 0) {
		if (page == start && page->next == NULL) {
			/* don't free the last page */
#ifdef MALLOC_CLOSURE_DEBUG
			printf("Don't free the very last page %p\n", page);
#endif
			return;
		}
		/* unlink the current page from the chain */
		if (page->next)
			page->next->prev = page->prev;
		if (page->prev) {
			page->prev->next = page->next;
		} else {
			start = page->next;
			if (start)
				start->prev = NULL;
			else
				Py_FatalError("ctypes: no free page left\n");
		}

		/* now, page can be freed */
		free_page(page);
#ifdef MALLOC_CLOSURE_DEBUG
		printf("FREEING page %p\n", page);
#endif
	}
}

void *MallocClosure(void)
{
	PAGE *page = start;
	int i;

	if (start == NULL)
		page = start = get_page();

	while(page) {
		if (page->used < page->count) {
			/* This page has a free entry */
			for (i = 0; i < page->count; ++i) {
				if (page->closure[i].cif == NULL) {
					page->closure[i].cif = (ffi_cif *)-1;
					++page->used;
					return &page->closure[i];
				}
			}
			/* oops, where is it? */
			Py_FatalError("ctypes: use count on page is wrong");
		}
		if (page->next)
			/* try the next page, if there is one */
			page = page->next;
		else {
			/* need a fresh page */
			PAGE *new_page = get_page();
			if (new_page == NULL)
				return NULL;
			/* insert into chain */
			new_page->prev = page;
			page->next = new_page;
			page = new_page;
		}
	}
	return NULL;
}
