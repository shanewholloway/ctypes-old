from ctypes.com import hresult
from ctypes.com.client import Dispatch

import unittest

class Word(unittest.TestCase):
    def test_word(self):
        try:
            word = Dispatch("Word.Application")
        except WindowsError, details:
            if details.errno == hresult.CO_E_CLASSSTRING:
                self.fail("It seems Word is not installed...")
            raise
        word.Visible = 1

        doc = word.Documents.Add()
        wrange = doc.Range()
        for i in range(10):
            wrange.InsertAfter("Hello from ctypes via COM %d\n" % i)
        paras = doc.Paragraphs

        for i in range(len(paras)):
            p = paras[i]()
            p.Font.ColorIndex = i+1
            p.Font.Size = 12 + (2 * i)

        doc.Close(SaveChanges=0)

        word.Quit()

if __name__ == '__main__':
    unittest.main()
