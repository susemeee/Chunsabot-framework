from decimal import *

class PI:
    #Sets decimal to 25 digits of precision
    getcontext().prec = 1000

    @staticmethod
    def factorial(n):
        # if n<1:
        #     return 1
        # else:
        #     return n * PI.factorial(n-1)
        result = 1
        for i in xrange(2, n+1):
            result *= i
        return result

    @staticmethod
    def plouffBig(n): #http://en.wikipedia.org/wiki/Bailey%E2%80%93Borwein%E2%80%93Plouffe_formula
        pi = Decimal(0)
        k = 0
        while k < n:
            pi += (Decimal(1)/(16**k))*((Decimal(4)/(8*k+1))-(Decimal(2)/(8*k+4))-(Decimal(1)/(8*k+5))-(Decimal(1)/(8*k+6)))
            k += 1
        return pi

    @staticmethod
    def bellardBig(n): #http://en.wikipedia.org/wiki/Bellard%27s_formula
        pi = Decimal(0)
        k = 0
        while k < n:
            pi += (Decimal(-1)**k/(1024**k))*( Decimal(256)/(10*k+1) + Decimal(1)/(10*k+9) - Decimal(64)/(10*k+3) - Decimal(32)/(4*k+1) - Decimal(4)/(10*k+5) - Decimal(4)/(10*k+7) -Decimal(1)/(4*k+3))
            k += 1
        pi = pi * 1/(2**6)
        return pi

    @staticmethod
    def chudnovskyBig(n): #http://en.wikipedia.org/wiki/Chudnovsky_algorithm
        pi = Decimal(0)
        k = 0
        while k < n:
            pi += (Decimal(-1)**k)*(Decimal(PI.factorial(6*k))/((PI.factorial(k)**3)*(PI.factorial(3*k)))* (13591409+545140134*k)/(640320**(3*k)))
            k += 1
        pi = pi * Decimal(10005).sqrt()/4270934400
        pi = pi**(-1)
        return pi

    @staticmethod
    def calculate():
        return PI.bellardBig(1000)
