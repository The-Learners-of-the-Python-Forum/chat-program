'''
Generic iterable utilities. These used to be contained in the main package.

AUTHORS:
v1.0.0+             --> pydsigner
'''

def replace_many(s, d, inverse = False):
    '''
    Goes through dict @d's keys and replaces their occurences with their 
    value. If @inverse is true, the values are replaced by the keys.
    NOTE: Results may vary from run to run and machine to machine because of 
    Python's dictionary optimization, especially if @inverse is true and some 
    keys have the same value. If @inverse is true, no empty strings can be 
    among the values, and if not, no empty string keys.

    >>> replace_many('quantum_junk10', {'1': '', '0': 'o', '_': ' '})
    'quantum junko'
    >>> replace_many('quantum_junk10', {'a': '0', 'b': '1'}, True)
    'quantum_junkba'
    >>> replace_many('quantum_junk10', {'': '5'})
    <TypeError traceback>

    AUTHORS:
    v0.2.0+             --> pydsigner
    '''
    if inverse:
        for k in d:
            s = s.replace(d[k], k)
    else:
        for k in d:
            s = s.replace(k, d[k])
    return s

def remove_many(s, l):
    '''
    Goes through every item of @l and removes their occurences in @s.
    
    >>> remove_many('quantum_junk10', '_0123456789')
    'quantumjunk'
    
    AUTHORS:
    v0.2.0+             --> pydsigner
    '''
    d = {}
    for i in l:
        d[i] = ''
    return replace_many(s, d)

def keep_many(s, l):
    '''
    Goes through @s and removes all chars that are not in @l.
    
    >>> keep_many('quantum_junk10', 'abcdefghijklmnopq')
    'qanmjnk'
    
    AUTHORS:
    v0.2.0-v0.3.6.3     --> pydsigner
    v0.3.7+             --> ffao/pydsigner'''
    return ''.join(c for c in s if c in l)

def section(itr, size):
    '''
    Goes through @itr and splits it up into chunks of @size.
    
    >>> section('quantum_junk10', 3)
    ['qua', 'ntu', 'm_j', 'unk', '10']
    
    AUTHORS:
    v0.3.1+             --> pydsigner
    '''
    r = itr[:]
    res = []
    while r:
        res.append(r[:size])
        r = r[size:]
    return res

def find(itr, value, *args, **kw):
    '''
    Just like str().find(), but also works for list()'s, which have a 
    .index() like str()'s do but no .find().
    
    AUTHORS:
    v0.4.4+         --> pydsigner
    '''
    try:
        return itr.index(value, *args, **kw)
    except ValueError:
        return -1

def flatten(obj, levels = -1):
    '''
    Flattens object @obj into a list. If an iterator, @obj will be recursed 
    up @levels times if @levels is not negative, else until there are no more 
    nested lists. If the recursion limit has been reached, a list() version of 
    @obj will be returned. If @obj is not an iterator, a list containing @obj 
    will be returned.
    
    >>> flatten(1)
    [1]
    >>> flatten([1, [2, [[[3, [[[4]]]]], 5, [6]]]]]])
    [1, 2, 3, 4, 5, 6]
    >>> flatten([1, [2, [3]], 4], 1)
    [1, 2, [3], 4]
    >>> l2 = l = [0]
    >>> l.append(l2)    # a recursive object!
    >>> flatten(l, 4)   # using recursion limits to avoid errors
    [0, 0, 0, 0, 0, [0, [...]]]
    
    AUTHORS:
    v0.4.8+         --> pydsigner
    '''
    if hasattr(obj, '__iter__'):
        if levels == 0:
            l = list(obj)
        else:
            lvl = levels - 1 if levels > 0 else levels
            l = sum((flatten(sl, lvl) for sl in obj), [])
    else:
        l = [obj]
    return l
