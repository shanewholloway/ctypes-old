"""
From: Robin Becker
Subject: Re: Understanding PyEval_InitThreads
Newsgroups: comp.lang.python
Date: Thu, 21 Nov 2002 10:55:13 +0000

...
On windows at least Thomas' test_enumwindows.py can be easily extended
to multithread and the results indicate that ctypes is preserving the
thread correctly in this case. (see test code below)
...
-- 
Robin Becker

"""

# Additional changes by Thomas Heller
####### hacked to use multiple threads by Robin Becker
# from Paul Moore via comp.lang.python
import thread, time
from ctypes import windll, CFuncPtr, c_string, c_int, FUNCFLAG_STDCALL
user32 = windll.user32

mutex = thread.allocate_lock()
count = 0

class EnumWindowsProc(CFuncPtr):
    _argtypes_ = c_int, c_int
    _flags_ = FUNCFLAG_STDCALL

def DisplayWindow(hwnd, lparam, where=None):
    title = c_string('\000' * 256)
    user32.GetWindowTextA(hwnd, title, 255)
    num = thread.get_ident()
    time.sleep(0.000001)        # Let other threads run
    print >>where, "Thread%d: hwnd=%08x title=%s" % (num,hwnd, repr(title.value))
    print "Thread%d: hwnd=%08x title=%s" % (num,hwnd, repr(title.value))

def run(num=0):
##    where = open('/tmp/test_enumwindows_out_%d.txt' % num,'w')
    where = None
    user32.EnumWindows(EnumWindowsProc(
        lambda x,y,where=where: DisplayWindow(x,y,where)), 0)
    mutex.acquire()
    global count
    count += 1
    mutex.release()
    print 'Thread%d num=%d finished!' % (thread.get_ident(), num)

def start(N):
    for num in xrange(N):
        thread.start_new_thread(run,(num,))

    #spin wait
    while 1:
        if mutex.acquire(0):
            if count==N:
                print 'Done!'
                mutex.release()
                break
            mutex.release()
        time.sleep(0.001)       # Let other threads run

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 5
    start(n)

################################################################
#
# Two types of errors when EnumWindowsProc(CFuncPtr) is used:
#
##Traceback (most recent call last):
##  File "C:\sf\ctypes_head\samples\Windows\test_enumwindows_mt.py", line 47, in <lambda>
##    lambda x,y,where=where: DisplayWindow(x,y,where)), 0)
##  File "C:\sf\ctypes_head\samples\Windows\test_enumwindows_mt.py", line 40, in DisplayWindow
##    print >>where, "Thread%d: hwnd=%08x title=%s" % (num,hwnd, repr(title.value))
##AttributeError: 'tuple' object has no attribute 'write'
##Thread2332: hwnd=000804c4 title=''

##Traceback (most recent call last):
##  File "C:\sf\ctypes_head\samples\Windows\test_enumwindows_mt.py", line 47, in <lambda>
##    lambda x,y,where=where: DisplayWindow(x,y,where)), 0)
##  File "C:\sf\ctypes_head\samples\Windows\test_enumwindows_mt.py", line 40, in DisplayWindow
##    print >>where, "Thread%d: hwnd=%08x title=%s" % (num,hwnd, repr(title.value))
##AttributeErrorFatal Python error: GC object already in linked list
