def fibGen(a,b):
    yield a     
    yield b     
    while True:         
        c = a + b         
        yield c         
        a = b         
        b = c