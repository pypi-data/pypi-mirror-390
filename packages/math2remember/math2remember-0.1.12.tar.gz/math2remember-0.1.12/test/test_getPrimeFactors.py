import sys
sys.path.append('../math2remember')
from math2remember.getPrimeFactors import getPrimeFactors

def testIsPrime():
    assert getPrimeFactors(12) == {'2':2, '3':1}
    assert getPrimeFactors(2) == {'2':1}
    assert getPrimeFactors(5) == {'5':1}
    assert getPrimeFactors(16) == {'2':4}
    assert getPrimeFactors(15) == {'3':1,'5':1}
    assert getPrimeFactors(30) == {'2':1,'3':1,'5':1}