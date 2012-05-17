'''
Module to make it easier to write code compatible with both 2.x and 3.x.

AUTHORS:
v0.2.0+         --> pydsigner
'''

import sys

__all__ = ['input', 'range', 'chr', 'str', 'Print']

try:
    input = raw_input
    range = xrange
    chr = unichr
    str = unicode

except NameError:
    pass

Print = __builtins__.get('print')
