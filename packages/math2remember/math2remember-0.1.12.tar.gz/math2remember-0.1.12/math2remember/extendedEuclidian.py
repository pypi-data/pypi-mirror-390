import math
def extendedEuclidian(a, b):
    if b == 0:
        return a, 1, 0
    '''
    Compute the extended euclidian algorithm.
    
    Parameters
    ----------
    a : int
        First integer.
    b : int
        Second integer.
        
    Returns
    -------
    gcd : int
        Greatest common divisor of `a` and `b`.
    x : int
        Bézout coefficient for `a`.
    y : int
        Bézout coefficient for `b`.
    
    
    Notes
    -----
    This method is based on gcd(a,b)=x*a+y*b.
    It makes use of the following statement gcd(a,b)=gcd(b,a%b)
    
    - a = q*b+r with q=⌊a/b⌋ -> r = a-q*b = a%b, q ∈ ℤ.
    - d | a -> a=m*d, d | b -> b=n*d, m,n ∈ ℤ.
    - d | a & d | b -> d | gcd(a,b)
    
    To show d | gcd(b,a%b).
    Proof: 
    gcd(b,a%b) = x1*b+y1*(a%b)=x1*b+y1*r
        =x1*b+y1*(a-q*b)=x1*(n*d)+y1*(m*d-q*n*d)
        =x1*n*d+y1*m*d-y1*q*n*d=d*(x1*n+y1*m-y1*q*n)
        -> d | gcd(b,a%b)
    '''
    gcd, x1, y1 = extendedEuclidian(b, a%b)
    '''
    We come back from the previous function call.
    Our goal is to create x and y from the known x1, y1.
    
    gcd = x1*b+y1*(a%b)=x1*b+y1*r=x1*b+y1*(a-q*b)
        = x1*b+y1*a-y1*q*b = y1*a+x1*b-y1*q*b
        = y1*a+(x1-y1*q)*b
        
        -> x = y1 & y = (x1-y1*q) with q = floor(a/b)
    '''
    x = y1
    y = x1 - y1*math.floor(a/b)
    return gcd, x, y