'''
Utility wrappers for places requiring functions, but where defining a new 
function would be overkill, lambdas would be plain annoying, and/or 
state-retention is desired.

AUTHORS:
0.3.9+          --> pydsigner
'''

class ValueWrapper(object):
    '''
    Makes a value look like a function. Use where a function is required to 
    return a value, but only one value is desired. If a reference is stored, a 
    new value could be set later.
    
    >>> v = ValueWrapper(5)
    >>> v()
    5
    >>> v.value = 7
    >>> v()
    7
    
    AUTHORS:
    0.3.9+          --> pydsigner
    '''
    def __init__(self, value):
        self.value = value
    def __call__(self):
        return self.value


class BumpWrapper(object):
    '''
    Similar to ValueWrapper(), but increments the value every time it is 
    called.
    
    >>> b = BumpWrapper(10, 4)
    >>> b()
    10
    >>> b()
    14
    >>> b()
    18
    
    AUTHORS:
    0.3.9+          --> pydsigner
    '''
    def __init__(self, value, inc):
        self.original_value = self.value = value
        self.inc = inc
        self.first = True
    
    def __call__(self):
        if self.first:
            self.first = False
        else:
            self.value += self.inc
        return self.value


class GiveCount(object):
    '''
    This wrapper is designed to go in places such as the "key" keyword 
    argument to max(), min(), and sort(). It counts the occurences of the 
    passed objects and returns that.
    
    >>> counter = GiveCount()
    >>> counter(GiveCount)
    1
    >>> counter(3)
    1
    >>> counter(GiveCount)
    2
    >>> # A special feature for special applications
    ... counter(GiveCount, -1)
    1
    
    AUTHORS:
    0.3.10+         --> pydsigner
    '''
    def __init__(self, inc = 1):
        self.d = {}
        self.inc = inc
    def __call__(self, obj, inc = None):
        v = inc if inc != None else self.inc
        if obj in self.d:
            v += self.d[obj]
        self.d[obj] = v
        return v
    
    def reset(self, inc = None):
        self.d = {}
        self.inc = inc if inc != None else self.inc
    def get_count(self, obj):
        self(obj, 0)
        return self.d[obj]


class CallWrapper(object):
    '''
    CallWrapper() is a decorator generator for decorators that wrap calls to 
    a function in another function. It has special features such as changing 
    the docstring to show help for the first function.
    
    AUTHORS:
    0.4.8+          --> pydsigner
    '''
    def __init__(self, funcs = []):
        '''
        Create a CallWrapper() with @funcs for callables. They will be called 
        in order, so that funcs[0] will be called with any passed variables, 
        and then funcs[1] will be called on the result of that and so on.
        '''
        self.funcs = funcs
        self.__doc__ = funcs[0].__doc__# + '\n\n*Wrapped with CallWrapper!*'
    
    def __repr__(self):
        return 'CallWrapper([%s])' % ', '.join(repr(r) for r in self.funcs)
    
    def __call__(self, *args, **kw):
        res = self.funcs[0](*args, **kw)
        for f in self.funcs[1:]:
            res = f(res)
        return res
