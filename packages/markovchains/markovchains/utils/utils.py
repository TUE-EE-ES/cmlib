""" miscellaneous utility functions """

from functools import reduce
from math import floor, gcd, log
from string import digits
import time
from fractions import Fraction
from typing import Callable, Iterable, List, Optional, Tuple, Union
import markovchains.utils.linalgebra as linalg
from markovchains.utils.statistics import StopConditions

NUM_FORMAT = '{:.5f}'
NUM_SCIENTIFIC = '{:.5e}'
COMPLEXITY_THRESHOLD: int = 50

# Frac = lambda n : Fraction(n).limit_denominator(max_denominator=1000000) if not np.isnan(n) else n

def warn(s: str):
    print("Warning: " + s)

def error(s: str):
    print("Error: "+ s)
    exit()

def onlyDigits(s: str)->str:
    return ''.join(c for c in s if c in digits)

def onlyNonDigits(s: str)->str:
    return ''.join(c for c in s if c not in digits)


def getIndex(name: str)->int:
    dig = onlyDigits(name)
    if dig == '':
        return -1
    else:
        return int(dig)

def isNumerical(setOfNames: Iterable[str])->bool:
    alphaNames = set([onlyNonDigits(s) for s in setOfNames])
    return len(alphaNames) <= 1

def stringToFloat(s: str, default: float)->float:
    try:
        return float(s)
    except ValueError:
        return default


def sortNames(setOfNames: Iterable[str])->List[str]:

    listOfNames = list(setOfNames)
    if isNumerical(setOfNames):
        listOfNames.sort(key=getIndex)
    else:
        listOfNames.sort()
    return listOfNames

def printList(l: List[float])->str:
    try:
        string = "["
        for item in l:
            string += NUM_FORMAT.format(item)+", "
        return string[:-2] + "]"
    except:
        return str(l)

def printOptionalList(l: Optional[List[float]], noneText: str = "--")->str:
    if l is None:
        return noneText
    return printList(l)



def printInterval(i: Tuple[float,float])->str:
    return printList([i[0],i[1]])

def printListOfIntervals(l: List[Tuple[float,float]])->str:
    try:
        string = "["
        for i in l:
            string += printInterval(i) + ", "
        return string[:-2] + "]"
    except:
        return str(l)

def printOptionalInterval(i: Optional[Tuple[float,float]])->str:
    if i is None:
        return "--"
    return printList([i[0],i[1]])

def printOptionalListOfIntervals(l: Optional[List[Tuple[float,float]]])->str:
    if l is None:
        return "--"
    return printListOfIntervals(l)
    
def optionalFloatOrStringToString(nr: Optional[Union[str,float]]):
    if nr is None:
        return "--"
    if isinstance(nr, str):
        return nr
    try:
        return NUM_FORMAT.format(nr)
    except:
        return "{}".format(nr)


def printSortedSet(s: Iterable[str]):
    print("{{{}}}".format(", ".join(sortNames(s))))

def printSortedList(s: Iterable[str]):
    print("{}".format(", ".join(sortNames(s))))

def printListOfStrings(s: List[str]):
    print ("[{}]\n".format(", ".join(s)))

def printTable(table: List[Union[str,List[str]]], margin: int = 1):

    # determine nr of columns of table
    nrColumns: int = -1
    for row in table:
        if isinstance(row, list):
            nrColumns = len(row)

    if nrColumns == -1:
        # table has no proper rows
        for row in table:
            print(row)
            return

    # determine column widths
    widths: List[int] = []
    for column in range(nrColumns):
        w: int = 0
        for row in table:
            if isinstance(row, list):
                w = max(w, len(row[column]))
        widths.append(w)
    
    # print the table
    for row in table:
        if isinstance(row, str):
            print(row)
        else:
            for i in range(len(row)):
                if i > 0:
                    print(" ".ljust(margin), end="")
                print(row[i].ljust(widths[i]), end="")
            print()

def stopCriteria(c: List[float])->StopConditions:
    # Format stop criteria: 
    stop = '''
    Steady state behavior = 
    [
        Confidence level,
        Absolute error,
        Relative error,
        Maximum path length,
        Maximum number of cycles,
        Time (in seconds)
    ]

    Transient behavior = 
    [
        Confidence level,
        Absolute error,
        Relative error,
        Maximum path length,
        Maximum number of paths,
        Time (in seconds)
    ]
    '''

    if len(c) != 6:
        s = "Wrong number of arguments for -c\n" + stop
        error(s)
    
    # Confidence level
    if c[0] <= 0:
        s = "No confidence level set"
        error(s)
    
    if all(i<=0 for i in c[1:]):
        s = "No stop conditions inside -c argument, simulation never terminating"
        error(s)
    
    return StopConditions(c[0],c[1], c[2], int(c[3]), int(c[4]), c[5])

def nrOfSteps(ns: int)->int:
    if ns == None:
        s = "Number of steps required (flag -ns)"
        error(s)
    if int(ns) < 1:
        s = "Number of steps must be at least 1"
        error(s)
    return ns

def vectorFloatToFraction(v: Iterable[float])->List[Fraction]:
    return [Fraction(e).limit_denominator(10000) for e in v] 

def matrixFloatToFraction(M: Iterable[Iterable[float]])->List[List[Fraction]]:
    return [[Fraction(e).limit_denominator(10000) for e in r] for r in M]

def lcm(a: int, b: int)->int:
    '''Least common multiple (does not exist in math library python version <=3.8)'''
    return abs(a*b) // gcd(a, b)

def commonDenominator(den: int, v: Fraction)->int:
    return lcm(den,v.denominator)

def commonDenominatorList(l: List[Fraction])->int:
    den: int = 1
    for v in l:
        den = commonDenominator(den, v)
    return den

def primeFactors(n: int)->List[int]:
    i = 2
    factors = []
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


def complexity(n: int):
    primeFactorList = primeFactors(n)
    if len(primeFactorList) == 0:
        return 1
    return len(primeFactorList)*max(primeFactorList)

def isComplex(n: int)->bool:
    return complexity(n)>COMPLEXITY_THRESHOLD

def vectorFractionToFloat(v: List[Fraction])->List[float]:
    return [float(e) for e in v]

def matrixFractionToFloat(M: List[List[Fraction]])->List[List[float]]:
    return [[float(e) for e in r] for r in M]

def prettyPrintMatrix(M: List[List[Fraction]]):
    '''Print matrix M to the console.'''
    
    # transform to row major for easy printing
    M = linalg.transpose(M)
    
    # get common denominator
    den: int = 1
    for r in M:
        den = lcm(den, commonDenominatorList(r))
    if isComplex(den):
        printMatrix(matrixFractionToFloat(M))
    else:
        printFractionMatrix(M)

def prettyPrintVector(v: List[Fraction]):
    # get common denominator
    den = commonDenominatorList(v)
    if isComplex(den):
        printVector(vectorFractionToFloat(v))
    else:
        printFractionVector(v)

def prettyPrintValue(x: Fraction, end=None):
    if isComplex(x.denominator):
        print(NUM_FORMAT.format(x), end=end)
    else:
        print(x, end=end)


def maxOpt(l: List[Optional[int]])-> Optional[int]:
    return reduce(lambda m, v: v if m is None else (m if v is None else max(v,m)), l, None)

def minOpt(l: List[Optional[int]])-> Optional[int]:
    return reduce(lambda m, v: v if m is None else (m if v is None else min(v,m)), l, None)

def exponent(e: Optional[float])->Optional[int]:
    if e is None:
        return None
    else:
        if e==0.0:
            return None
        return floor(log(abs(e), 10.0))


def determineMaxExp(M: List[List[float]]):
    mo = maxOpt([maxOpt([exponent(e) for e in r]) for r in M])
    if mo is None:
        return 0
    return mo

def determineMaxExpVector(v: List[float]):
    mo = maxOpt([exponent(e) for e in v])
    if mo is None:
        return 0
    return mo

def determineMinExp(M: List[List[float]]):
    mo = minOpt([minOpt([exponent(e) for e in r]) for r in M])
    if mo is None:
        return 0
    return mo

def expMatrix(M: List[List[float]], ex: int) -> List[List[float]]:
    f = pow(10,ex)
    return [[e * f for e in r] for r in M]

def expVector(v: List[float], ex: int) -> List[float]:
    f = pow(10,ex)
    return [e * f for e in v]

def elementToString(x: float, w: Optional[int]=None)->str:
    ex = 0 if x==0.0 else log(abs(x),10)
    fmt = NUM_FORMAT if -3 <= ex <= 5 else NUM_SCIENTIFIC 
    return rightAlign(fmt.format(float(x)),w) if w else fmt.format(float(x))

def rightAlign(s: str, w: int)->str:
    return (' '*(w-len(s)))+s

def determineFractionWidth(e: Fraction)->int:
    return len('{}'.format(e))

def determineMaxFractionWidth(M: List[List[Fraction]])->Optional[int]:
    return maxOpt([determineMaxFractionWidthVector(r) for r in M])

def determineMaxFractionWidthVector(v: List[Fraction])->Optional[int]:
    return maxOpt([determineFractionWidth(e) for e in v])

def determineWidth(e: float)->int:
    return len(elementToString(e))

def determineMaxWidth(M: List[List[float]])->Optional[int]:
    return maxOpt([determineMaxWidthVector(r) for r in M])

def determineMaxWidthVector(v: List[float])->Optional[int]:
    return maxOpt([determineWidth(e) for e in v])

def vectorToString(v: List[float], w: Optional[int]=None)->str:
    '''Return string representation of the vector v.'''
    if w is None:
        w = determineMaxWidthVector(v)
    return '[ {} ]'.format(' '.join([elementToString(x,w) for x in v]))

def printMatrixWithExponent(M: List[List[float]], ex: int):

    M = expMatrix(M, -ex)

    expPrefix = '10^{} x '.format(ex)
    spcPrefix = ' ' * (len(expPrefix)+1)

    w: Optional[int] = determineMaxWidth(M)
    for i, v in enumerate(M):
        if i == 0:
            print(expPrefix+'[', end="")
        else:
            print(spcPrefix, end="")
        print(vectorToString(v, w), end='')
        if i < len(M)-1:
            print('')
        else:
            print(']')

def printVectorWithExponent(v: List[float], ex: int):

    v = expVector(v, -ex)

    expPrefix = '10^{} x '.format(ex)

    w: Optional[int] = determineMaxWidthVector(v)
    print(expPrefix, end="")
    print(vectorToString(v, w), end='')

def printVector(v: List[float]):
    if len(v) == 0:
        print('[]')
        return
    maxE: int = determineMaxExpVector(v)
    if maxE > 3 or maxE < -2:
        printVectorWithExponent(v, maxE)
        return

    w: Optional[int] = determineMaxWidthVector(v)
    print(vectorToString(v, w))

def printMatrix(M: List[List[float]]):
    '''Print matrix M to the console.'''
    if len(M) == 0:
        print('[[]]')
        return
    maxE: int = determineMaxExp(M)
    if maxE > 3 or maxE < -2:
        printMatrixWithExponent(M, maxE)
        return

    w: Optional[int] = determineMaxWidth(M)
    for i, v in enumerate(M):
        if i == 0:
            print('[', end="")
        else:
            print(' ', end="")
        print(vectorToString(v, w), end='')
        if i < len(M)-1:
            print('')
        else:
            print(']')

def elementToFractionString(x: Fraction, w: Optional[int]=None)->str:
    return rightAlign('{}'.format(x), w) if w else '{}'.format(x)

def vectorToFractionString(v: List[Fraction], w: Optional[int]=None)->str:
    '''Return string representation of the vector v.'''
    if w is None:
        w = determineMaxFractionWidthVector(v)
    return '[ {} ]'.format('  '.join([elementToFractionString(x, w) for x in v]))

def printFractionMatrix(M: List[List[Fraction]]):
    '''Print matrix M to the console.'''
    if len(M) == 0:
        print('[[]]')
        return
    w: Optional[int] = determineMaxFractionWidth(M)
    for i, v in enumerate(M):
        if i == 0:
            print('[', end="")
        else:
            print(' ', end="")
        print(vectorToFractionString(v, w), end='')
        if i < len(M)-1:
            print('')
        else:
            print(']')

def printFractionVector(v: List[Fraction]):
    if len(v) == 0:
        print('[]')
        return
    w: Optional[int] = determineMaxFractionWidthVector(v)
    print(vectorToFractionString(v, w))

class TimeoutTimer(object):
    
    _secondsTimeout: float
    _initialTime: float
    _active: bool

    def __init__(self, secondsTimeOut: float) -> None:
        self._secondsTimeout = secondsTimeOut
        self._active = secondsTimeOut > 0.0
        self._initialTime = time.time()

    def isExpired(self)->bool:
        if self._active:
            return self._secondsTimeout <= time.time() - self._initialTime
        return False

    def simAction(self)-> Callable[[int,str],bool]:
        if self._active:
            return lambda n, state: self._secondsTimeout <= time.time() - self._initialTime
        return lambda n, state: False
