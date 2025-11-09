import sys
sys.path.append('../math2remember')
from math2remember.fibGen import fibGen

def testIsPrime():
    g = fibGen(1,2)
    assert [1,2,3,5,8,13,21,34,55,89] == [next(g) for _ in range(10)] 