from COM import Dispatch
##from win32com.client.dynamic import Dispatch

def test_word():
    try:
        word = Dispatch("Word.Application")
    except WindowsError, details:
        if details.errno == 0x800401F3: # Invalid Class String
            print "It seems Word is not installed..."
            return
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

    import time
    time.sleep(1)

    doc.Close(SaveChanges=0)

    word.Quit()

if __name__ == '__main__':
    test_word()
