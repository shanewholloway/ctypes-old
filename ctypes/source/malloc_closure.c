/* Allocate executable memory */
#include <Python.h>
#include <ffi.h>
#include "ctypes.h"

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
	int count;
	ffi_closure closure[0];
} PAGE;

PAGE *start;
unsigned int pagesize;

static PAGE *get_page()
{
	PAGE *page;
#ifdef MS_WIN32
	if (!pagesize) {
		SYSTEM_INFO systeminfo;
		GetSystemInfo(&systeminfo);
		pagesize = systeminfo.dwPageSize;
	}
	
	page = (PAGE *)VirtualAlloc(NULL,
				    pagesize,
				    MEM_COMMIT,
				    PAGE_EXECUTE_READWRITE);
	if (page == NULL)
		return NULL;
#else
	if (!pagesize) {
		pagesize = sysconf(_SC_PAGESIZE);
	}
	page = (PAGE *)mmap(NULL,
			    pagesize,
			    PROT_READ | PROT_WRITE | PROT_EXEC,
			    MAP_PRIVATE | MAP_ANONYMOUS,
			    -1,
			    0);
	if (page == (void *)MAP_FAILED)
		return NULL;
	memset(page, 0, pagesize);
#endif
	page->count = (pagesize - sizeof(page)) / sizeof(ffi_closure);

#ifdef MALLOC_CLOSURE_DEBUG
	page->count = 5;

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
	if (-1 == munmap((void *)page, pagesize))
		Py_FatalError("ctypes: executable memory head corrupted");
#endif
}

void FreeClosure(void *p)
{
	PAGE *page = start;
	PAGE *prev = NULL;
	ffi_closure *pcl = (ffi_closure *)p;
	int i;
	int isfree;

	while(page) {
		isfree = 1;
		for (i = 0; i < page->count; ++i) {
			if (page->closure[i].cif)
				isfree = 0;
			if (&page->closure[i] == pcl) {
				page->closure[i].cif = NULL;
				return;
			}
		}
		if (isfree) {
			PAGE *tmp = page;

			/* unlink the current page from the chain */
			if (prev)
				prev->next = page->next;
			else
				start = page->next;
			page = page->next;
			/* now, page can be freed */
			free_page(tmp);
#ifdef MALLOC_CLOSURE_DEBUG
			printf("FREEING page %p\n", tmp);
#endif
		} else {
			prev = page;
			page = page->next;
		}
	}
	Py_FatalError("ctypes: closure not found in heap");
}

void *MallocClosure(void)
{
	PAGE *page = start;
	int i;

	if (page == NULL)
		start = page = get_page();

	while(page) {
		for (i = 0; i < page->count; ++i) {
			if (page->closure[i].cif == NULL) {
				page->closure[i].cif = (ffi_cif *)-1;
				return &page->closure[i];
			}
		}
		if (page->next)
			page = page->next;
		else {
			PAGE *next = get_page();
			if (next == NULL)
				return NULL;
			page->next = next;
			page = next;
		}
	}
	return NULL;
}
