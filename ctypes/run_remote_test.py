import os, sys, unittest

if __name__ == "__main__":
    dirname, filename = os.path.split(sys.argv[1])
    basename, ext = os.path.splitext(filename)

    del sys.argv[1]
    sys.path.append(dirname)

    runner = unittest.TextTestRunner(open("test.output", "w"), verbosity=2)
    unittest.main(module=__import__(basename), testRunner=runner)
