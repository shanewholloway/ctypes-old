# superseeded by test_numbers.py
import unittest

def get_suite():
    return None

def test(verbose=0):
    runner = unittest.TextTestRunner(verbosity=verbose)
    runner.run(get_suite())

if __name__ == '__main__':
    unittest.main()
