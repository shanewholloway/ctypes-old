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
from ctypes import windll, CFunction, c_string
user32 = windll.user32

mutex = thread.allocate_lock()
count = 0

class EnumWindowsProc(CFunction):
    _types_ = "ii"
    _stdcall_ = 1

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
