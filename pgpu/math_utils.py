'''
Utilities to work with bases plus some trig utilities and a more powerful
version of decimal.Decimal().

AUTHORS:
v0.2.0+         --> pydsigner
'''

import string
import math
from fractions import Fraction as frac
import cmath
import operator
import decimal

import iter_utils
from compatibility import range

# should we use string.ascii_uppercase?
DEFAULT_REP_ORDER = string.digits + string.ascii_lowercase


def convert_to_base(b10int, base):
    '''
    Convert base 10 integer @b10int to base @base.
    
    >>> convert_to_base(400, "10", "9876543210")
    "699"
    >>> convert_to_base("10", 2)
    "1010"
    >>> convert_to_base(340.4, 30)
    "ab"
    
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    # We aren't going to try to convert floats. (Todo or fail?)
    uint = int(b10int)
    # We certainly aren't going to use float bases! (Fail?)
    ubase = abs(int(base))  
    res = ''
    sign = ''
    if uint < 0:
        uint = abs(uint)
        sign = '-'
    elif uint == 0:
        return DEFAULT_REP_ORDER[0]
    while 1:
        res = DEFAULT_REP_ORDER[uint % ubase] + res
        uint //= ubase
        if uint == 0:
            break
    return sign + res


def sgp_with_base(b10int, base):
    '''
    SGP stands for smallest greater power. This function returns and number
    so that @base to the return value (i)-th power is greater than @b10int
    and @base ** (i - 1) is not.
    
    >>> sgp_with_base(3256, 5)
    6
    >>> 6 ** 5
    7776
    >>> 6 ** 4
    1296

    AUTHORS:
    v0.2.0-v0.3.7   --> pydsigner
    v0.3.8+         --> ffao
    '''
    return int(math.log(b10int, base)) + 1


def legs(hyp, ratio = (1, 1)):
    '''
    Calculates the leg lengths of a triangle with a hypotenuse of @hyp where
    the side length ratio is @ratio. Nice for calculating screen dimensions.
    
    >>> legs(15, [9, 16])
    (7.353918594488384, 13.073633056868239)
    
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    r = float(ratio[0]) / ratio[1]
    l2 = hyp / math.sqrt(r ** 2 + 1)
    l1 = l2 * r
    return l1, l2


def euclidean_dist(c1, c2):
    '''
    Returns the Euclidean distance between coordinate @c1 and @c2.
    
    >>> euclidean_dist((4, 6), (9, -10))
    16.76305461424021
    
    AUTHORS:
    v0.2.0+         --> pydsigner'''
    return math.hypot(c1[0] - c2[0], c1[1] - c2[1])


def sane_hex(v):
    '''
    Returns a more usable hex representation of int()'ed @v.
    
    >>> sane_hex(-846)
    '-34e'
    
    AUTHORS:
    v0.3.3+         --> pydsigner'''
    i = int(v)
    sign = '-' if i < 0 else ''
    i = abs(i)
    h = iter_utils.keep_many(hex(i), string.hexdigits).lstrip('0') or '0'
    return sign + h


def limit(val, bottom = None, top = None):
    '''Will return a copy of @val in such a way that:
    If @bottom is not None, the result will be no less that @bottom;
    If @top is not None, the result will be no more that @top.
    
    >>> limit(10)
    10
    >>> limit(10, 1)
    10
    >>> limit(10, 15)
    15
    >>> limit(10, 1, 8)
    8
    >>> # Can be used with anything that can be compared using max() and min()
    ... limit('6', None, '3')
    '3'
    
    AUTHORS:
    v0.4.5+         --> pydsigner
    '''
    uval = val
    if bottom is not None:
        uval = max(uval, bottom)
    if top is not None:
        uval = min(uval, top)
    return uval


def pascals_triangle(depth):
    '''
    Calculate Pascal's triangle to @depth places. returns a list of lists.
    
    >>> pascals_triangle(5)
    [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]]
    
    AUTHORS:
    v0.4.7+         --> pydsigner
    '''
    res = []
    for i in range(depth):
        row = [1]
        for c in range(1, i + 1):
            row.append(sum(res[-1][c - 1:c + 1]))
        res.append(row)
    return res


def to_polar(vec):
    '''
    Returns rectangular vector @vec as a polar coordinate represented as a 
    (distance, angle) tuple.
    
    AUTHORS:
    v0.4.7+         --> pydsigner
    '''
    return cmath.polar(complex(vec[0], vec[1]))


def to_vector(polar):
    '''
    Returns polar coordinate tuple @polar as a Vector().
    
    AUTHORS:
    v0.4.7+         --> pydsigner
    '''
    i = cmath.rect(*polar)
    return Vector(i.real, i.imag)


def rotate_vector(vec, degrees):
    '''
    Rotates rectangular vector @vec @degrees.
    NOTE: Use Vector().rotated() instead, which this simply wraps!
    
    AUTHORS:
    v0.4.7+         --> pydsigner
    v1.0.0+         --> pydsigner
    '''
    return Vector(vec).rotated(degrees)


def factors(n):
    '''
    Returns an set of every factor of @n (including 1 and @n).
    
    AUTHORS:
    v0.4.9+         --> pydsigner
    '''
    return set((x for x in range(1, int(n ** .5) + 2) if not n % x)) | set([n])


def polyroots(q, p, pol):
    '''
    Finds all of the roots of polynomial @pol, with the constant of highest 
    degree @q and the constant of x**0 @p. Returns a set of all the roots.
    
    >>> polyroots(1, 2, 'x**3 - 2*x**2 - x + 2')
    set([1, 2, -1])
    
    TODO: Add ability to find @q and @p from @pol
    
    AUTHORS:
    v0.5.1+         --> pydsigner
    '''
    s = set((x for x in set(iter_utils.flatten((((frac(up, uq) for uq, up in [
                    (-qv, -pv), (-qv, pv), (qv, -pv), (qv, pv)]) 
                for qv in factors(abs(q))) for pv in factors(abs(p))))) 
            if eval(pol.replace('x', 'frac("%s")' % x)) == 0))
    
    nset = set()
    for n in s:
        if n.denominator == 1:
            nset.add(n.numerator)
        elif frac(float(n)) == n:
            nset.add(float(n))
        else:
            nset.add(n)
    return nset


class ExtendedDecimal(decimal.Decimal):
    '''
    An Extended version of decimal.Decimal(), with more geometric features,
    similar to those found in the standard math module. These features
    currently are:
        pi() (slightly modified from the decimal documentation)
        cos() (ibid)
        sin() (ibid)
        radians()
        degrees()
        tan()

    AUTHORS:
    v0.4.0+         --> pydsigner
    '''
    def __repr__(self):
        '''
        eval(repr(exdec)) <--> exdec
        
        AUTHORS:
        v0.4.1+         --> pydsigner
        '''
        return 'ExtendedDecimal(\'%s\')' % str(self)

    def pi(self):
        '''
        Compute Pi to the current precision.
        
        AUTHORS:
        v0.4.0+         --> pydsigner
        '''
        decimal.getcontext().prec += 2  # extra digits for intermediate steps
        three = decimal.Decimal(3)
        lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
        while s != lasts:
            lasts = s
            n, na = n+na, na+8
            d, da = d+da, da+32
            t = (t * n) / d
            s += t
        decimal.getcontext().prec -= 2  # reset precision
        return ExtendedDecimal(s)       # don't return a Decimal() instance!

    def cos(self):
        '''
        Return the cosine of self as measured in radians.
        
        AUTHORS:
        v0.4.0+         --> pydsigner
        '''
        decimal.getcontext().prec += 2
        i, lasts, s, fact, num, sign = 0, 0, 1, 1, 1, 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i-1)
            num *= self * self
            sign *= -1
            s += num / fact * sign
        decimal.getcontext().prec -= 2
        return ExtendedDecimal(+s)

    def sin(self):
        '''
        Return the sine of self as measured in radians.
        
        AUTHORS:
        v0.4.0+         --> pydsigner
        '''
        decimal.getcontext().prec += 2
        i, lasts, s, fact, num, sign = 1, 0, self, 1, self, 1
        while s != lasts:
            lasts = s
            i += 2
            fact *= i * (i-1)
            num *= self * self
            sign *= -1
            s += num / fact * sign
        decimal.getcontext().prec -= 2
        return ExtendedDecimal(s)

    def tan(self):
        '''
        Returns the tangent of self as measured in radians.
        
        AUTHORS:
        v0.4.1+         --> pydsigner
        '''
        return ExtendedDecimal(self.sin() / self.cos())

    def radians(self):
        '''
        returns self (as in degrees) in radians.
        AUTHORS:
        v0.4.0+         --> pydsigner
        '''
        return ExtendedDecimal(self * self.pi() / 180)

    def degrees(self):
        '''
        returns self (as in radians) in degrees.
        AUTHORS:
        v0.4.0+         --> pydsigner
        '''
        return ExtendedDecimal(self * 180 / self.pi())


class Vector(object):
    '''
    2d vector class, supports vector and scalar operators, and also provides
    a bunch of high level functions.
    NOTE: This was taken from Eli Bendersky, who took it from the Pygame Wiki
    (http://pygame.org/wiki/2DVectorClass). It was also slightly modified to be
    cross version compatible, be more sane, fit in with pgpu, and be more 
    useful. I opted for this implementation over my own because this was more 
    complete.
    
    AUTHORS:
    v0.4.3+         --> Pygame Wiki/pydsigner
    v1.0.0+         --> Pygame Wiki/pydsigner
    '''
    __slots__ = ['x', 'y']
    def __init__(self, x_or_pair = None, y = None):
        if y == None:
            if x_or_pair == None:
                self.x = self.y = 0
            else:
                self.x = x_or_pair[0]
                self.y = x_or_pair[1]
        else:
            self.x = x_or_pair
            self.y = y

    def __len__(self):
        return 2
    def __iter__(self):
        return iter((self.x, self.y))

    def __getitem__(self, key):
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise IndexError('Invalid subscript %s to Vector' % key)

    def __setitem__(self, key, value):
        if key == 0:
            self.x = value
        elif key == 1:
            self.y = value
        else:
            raise IndexError('Invalid subscript %s to Vector' % key)

    # String representation (for debugging)
    def __repr__(self):
        return 'Vector(%s, %s)' % (self.x, self.y)

    # Comparison
    def __eq__(self, other):
        if hasattr(other, '__getitem__') and len(other) == 2:
            return self.x == other[0] and self.y == other[1]
        else:
            return False

    def __ne__(self, other):
        if hasattr(other, '__getitem__') and len(other) == 2:
            return self.x != other[0] or self.y != other[1]
        else:
            return True

    def __nonzero__(self):
        return self.x or self.y
    __bool__ = __nonzero__      # for those poor 3.x users ;-) -- pydsigner

    # Generic operator handlers
    def _o2(self, other, f):
        '''
        Any two-operator operation where the left operand is a Vector
        '''
        if isinstance(other, Vector):
            return Vector(f(self.x, other.x),
                         f(self.y, other.y))
        elif (hasattr(other, '__getitem__')):
            return Vector(f(self.x, other[0]),
                         f(self.y, other[1]))
        else:
            return Vector(f(self.x, other),
                         f(self.y, other))

    def _r_o2(self, other, f):
        '''
        Any two-operator operation where the right operand is a Vector
        '''
        if (hasattr(other, '__getitem__')):
            return Vector(f(other[0], self.x),
                         f(other[1], self.y))
        else:
            return Vector(f(other, self.x),
                         f(other, self.y))

    def _io(self, other, f):
        '''
        inplace operator
        '''
        if (hasattr(other, '__getitem__')):
            self.x = f(self.x, other[0])
            self.y = f(self.y, other[1])
        else:
            self.x = f(self.x, other)
            self.y = f(self.y, other)
        return self

    # Addition
    def __add__(self, other):
        return self._o2(other, operator.add)
    def __radd__(self, other):
        return self._r_o2(other, operator.add)
    def __iadd__(self, other):
        return self._io(other, operator.add)

    # Subtraction
    def __sub__(self, other):
        return self._o2(other, operator.sub)
    def __rsub__(self, other):
        return self._r_o2(other, operator.sub)
    def __isub__(self, other):
        return self._io(other, operator.sub)

    # Multiplication
    def __mul__(self, other):
        return self._o2(other, operator.mul)
    def __rmul__(self, other):
        return self._r_o2(other, operator.mul)
    def __imul__(self, other):
        return self._io(other, operator.mul)

    # Division
    def __div__(self, other):
        return self._o2(other, operator.div)
    def __rdiv__(self, other):
        return self._r_o2(other, operator.div)
    def __idiv__(self, other):
        return self._io(other, operator.div)

    def __floordiv__(self, other):
        return self._o2(other, operator.floordiv)
    def __rfloordiv__(self, other):
        return self._r_o2(other, operator.floordiv)
    def __ifloordiv__(self, other):
        return self._io(other, operator.floordiv)

    def __truediv__(self, other):
        return self._o2(other, operator.truediv)
    def __rtruediv__(self, other):
        return self._r_o2(other, operator.truediv)
    def __itruediv__(self, other):
        return self._io(other, operator.truediv)

    # Modulo
    def __mod__(self, other):
        return self._o2(other, operator.mod)
    def __rmod__(self, other):
        return self._r_o2(other, operator.mod)

    def __divmod__(self, other):
        return self._o2(other, operator.divmod)
    def __rdivmod__(self, other):
        return self._r_o2(other, operator.divmod)

    # Exponentation
    def __pow__(self, other):
        return self._o2(other, operator.pow)
    def __rpow__(self, other):
        return self._r_o2(other, operator.pow)

    # Bitwise operators
    def __lshift__(self, other):
        return self._o2(other, operator.lshift)
    def __rlshift__(self, other):
        return self._r_o2(other, operator.lshift)

    def __rshift__(self, other):
        return self._o2(other, operator.rshift)
    def __rrshift__(self, other):
        return self._r_o2(other, operator.rshift)

    def __and__(self, other):
        return self._o2(other, operator.and_)
    __rand__ = __and__

    def __or__(self, other):
        return self._o2(other, operator.or_)
    __ror__ = __or__

    def __xor__(self, other):
        return self._o2(other, operator.xor)
    __rxor__ = __xor__

    # Unary operations
    def __neg__(self):
        return Vector(operator.neg(self.x), operator.neg(self.y))

    def __pos__(self):
        return Vector(operator.pos(self.x), operator.pos(self.y))

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y))

    def __invert__(self):
        return Vector(-self.x, -self.y)

    # vectory functions
    def get_length_sqrd(self):
        return self.x ** 2 + self.y ** 2

    def get_length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def __setlength(self, value):
        length = self.get_length()
        self.x *= value/length
        self.y *= value/length
    length = property(get_length, __setlength, None, 
                'gets or sets the magnitude of the vector')

    def rotate(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        self.x = x
        self.y = y

    def rotated(self, angle_degrees):
        radians = math.radians(angle_degrees)
        cos = math.cos(radians)
        sin = math.sin(radians)
        x = self.x * cos - self.y * sin
        y = self.x * sin + self.y * cos
        return Vector(x, y)

    def get_angle(self):
        if (self.get_length_sqrd() == 0):
            return 0
        return math.degrees(math.atan2(self.y, self.x))
    
    def __setangle(self, angle_degrees):
        self.x = self.length
        self.y = 0
        self.rotate(angle_degrees)
    angle = property(get_angle, __setangle, None, 
                'gets or sets the angle of a vector')

    def get_angle_between(self, other):
        cross = self.x * other[1] - self.y * other[0]
        dot = self.x * other[0] + self.y * other[1]
        return math.degrees(math.atan2(cross, dot))

    def normalized(self):
        length = self.length
        if length != 0:
            return self / length
        return Vector(self)

    def normalize_return_length(self):
        length = self.length
        if length != 0:
            self.x /= length
            self.y /= length
        return length

    def perpendicular(self):
        return Vector(-self.y, self.x)

    def perpendicular_normal(self):
        length = self.length
        if length != 0:
            return Vector(-self.y / length, self.x / length)
        return Vector(self)

    def dot(self, other):
        return float(self.x * other[0] + self.y * other[1])

    def get_distance(self, other):
        return euclidean_dist(self, other)

    def get_dist_sqrd(self, other):
        return (self.x - other[0])**2 + (self.y - other[1])**2

    def projection(self, other):
        other_length_sqrd = other[0]*other[0] + other[1]*other[1]
        projected_length_times_other_length = self.dot(other)
        return other*(projected_length_times_other_length/other_length_sqrd)

    def cross(self, other):
        return self.x*other[1] - self.y*other[0]

    def interpolate_to(self, other, range):
        return Vector(self.x + (other[0] - self.x) * range, 
                self.y + (other[1] - self.y) * range)

    def convert_to_basis(self, x_vector, y_vector):
        return Vector(self.dot(x_vector) / x_vector.get_length_sqrd(), 
                self.dot(y_vector) / y_vector.get_length_sqrd())

    def __getstate__(self):
        return [self.x, self.y]

    def __setstate__(self, dict):
        self.x, self.y = dict
