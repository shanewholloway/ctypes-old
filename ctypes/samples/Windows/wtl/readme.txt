Lectori Salutem,

This directory contains an experiment to create
a small template library to build GUI windows applications
using only pure python and the win32 API.
The windows API is called trough the use of Thomas Hellers's
excelent ctypes module.

The spirit of these components is about the same as that
of the Microsoft ATL and WTL libraries for C++. (e.g. low runtime
requirements, toolkit style, no doc/view paradigms etc).

It is still my believe that the best Windows Apps are build
using the RAW windows API using only small wrapper libraries such
as ATL or WTL.

The goals of this work is to:

- make it possible to make good-looking (at least on par with what is possible with C++/WTL/Win32)
  python based windows applications

- with the least amount of run-time needed. What I mean by this is that a distribution version of
  such a python windows application would only need the PythonXX.dll and the ctypes dll + the 
  pyc sources of the app itself.
  If this is not the case than it would not make sense to build this gui lib 
  (just use .NET then, and distribute the 20mb runtime with it (or Java with its 10mb runtime))
  So small is really the key here

- abstract some of the more anoying details of the win32 API. (but not all)

- abstraction 1:

	  The mapping from Win32 handles to real python instances of
	  a python Window class. The abstraction does not have to be 100% python,
	  I don't mind working with Msg Maps. If you would abstract these away
	  using some elaborate signal/slot/listener/bla mechanism, 10 to 1 that someday (sooner
	  rather than later) you would still have to deal with the gory details of Global Wnd Procs
	  and such anyway. 
	  
	  This is mostly implemented by using a global python dict which maps between HWNDS and instances
		(changed to WeakDict)

	  Msg cracking/routing is now handled trough a MSG_MAP class, different type of 'handlers'
	  are defined for processing Notification msgs, Command msg and normal WM_* msgs
	  
- abstraction 2:

	  Garbage collection. Most windows widgets (windows, menus, etc etc) have some CreateXXX
	  method and some special DestroyXXX method.
	  I would like these to be called automatically by the framework.
	  
	  This is not implemented yet, I've made a 'disposable' base class of which all things
	  with handles are derived. All derived classes implement a __dispose__(self) method
	  which calls the apropriate windows DestroyXXX function to release the handle.
	  At the moment these are called from the __del__ finalizer of 'disposable'. This
	  is not really working, and some design/thought must be put into this.

	  (Changed global dict to WeakValueDict, garbage collection mostly works, some
	  problems with static class members)
	  
	  
- abstraction 3:

	  Automatic Layout management. This is really lacking in the Windows API. It would be nice
	  to have. (see Swing for Java, it really works there).	  
	  
  
- based on the above, an optional library of controls:

right now i have:

form.py: 
	A form style main window. Automatically keeps track of other frame windows, closes
	the app  when last form is closed.

notebook.py :
	a 'Notebook' control. This is based on the TabControl common control. I contains some
	hacks to reduce the TabControl's flicker. It automatically hides and unhides the tab panes

tree.py: extended from TreeView common control. Contains some extra methods to make it more pythonic
list.py extended from ListView common control. Contains some extra methods to make it more pythonic

splitter.py: A usefull  window splitter class (Windows does not have this, so every toolkit needs its own).				
  
Try any of the 

test_*.py files to see the results sofar.

the COM.py file is the original by Thomas Heller with some additions by me 
for controling the Webbrowser control. This will be removed in the future
as COM support in ctypes matures.

Grtz,

Henk Punt

henk@entree.nl

