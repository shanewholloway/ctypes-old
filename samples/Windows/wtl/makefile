clean:
	find -name *~ -exec rm -rf {} \;	
	find -name *.pyc -exec rm -rf {} \;

clean_cvs:
	find -name CVS -exec rm -rf {} \;

test:
	find -name *.py -exec wc -l {} \;

dist: clean
	cd ..; tar -czf wtl.tgz wtl

exetest:
	python setup.py py2exe --icon blinky.ico