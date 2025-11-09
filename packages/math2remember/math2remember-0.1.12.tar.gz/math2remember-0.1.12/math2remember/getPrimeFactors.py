from .isPrime import isPrime
from .getPrimeGen import getPrimeGenTo

def getPrimeFactors(n):
    '''
    Computes prime factors of an number.
    
    Args:
        n: Positive integer (> 1)
        
    Returns:
        Dictionary with prime factors as keys and exponentes as vals.
        E.g.: 12 -> {2: 2, 3: 1}
        
    Raises:
        ValueError: If n < 2
    '''
    if n < 2:
        raise ValueError('n < 2')
    
    if isPrime(n):
        return {str(n):1}
    ret = {}
    primes = getPrimeGenTo(n)
    for prime in primes:
        while n%prime==0:

            try:
                ret[str(prime)] += 1
            except KeyError:
                ret[str(prime)] = 1 
            
            n /= prime # n = int(n/prime)
            
    return ret