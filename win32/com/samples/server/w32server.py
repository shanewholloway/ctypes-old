class Server:
    _reg_progid_ = "Test.Server"
    _reg_clsid_ = '{d0329e37-14c1-4d71-a4d8-df9534c7ebdf}'
    _public_methods_ = ["test"]

    def test(self):
        return 42

if __name__ == "__main__":
    from win32com.server.register import UseCommandLine
    UseCommandLine(Server)
    
