import sys
sys.path.append('../math2remember')
from math2remember.extendedEuclidian import extendedEuclidian

def testExtendedEuclidian():
    gcd, x, y = extendedEuclidian(4,2)
    assert gcd == 2
    assert x == 0
    assert y == 1
    gcd, x, y = extendedEuclidian(15,45)
    assert gcd == 15
    assert x == 1
    assert y == 0


                                        