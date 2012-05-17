'''
A unified interface to builtin hashers and codecs as well as some of my own.

AUTHORS:
v0.2.0+         --> pydsigner
'''

import hashlib
import base64
import zlib
import binascii

try:
    import urllib.parse as urler
except ImportError:
    import urllib as urler

import random
import math
import time
import decimal
from decimal import Decimal as dec
import string

import iter_utils
from compatibility import str, range, chr
from math_utils import sane_hex

__all__ = ['rand_key', 'multi_pass', 'encoder_classes', 'fetcher']
encoder_classes = {}


class Triplets(object):
    '''
    An encoder useful mostly for minor ciphers or sending information in a 
    format using a small amount of different characters.
    
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return '.'.join([str(ord(c) * 3) for c in s])
    def decode(self, s):
        return ''.join([chr(int(c) // 3) for c in s.split('.')])
__all__.append('Triplets')
encoder_classes['triplets'] = Triplets


class PD2(object):
    '''
    A basic hasher based on PD1(), but with many improvements. This is only 
    recommended for checksums: for passwords, PD6 or a more common hasher 
    should be used.
    
    AUTHORS:
    v0.2.4+         --> pydsigner
    '''
    mag_num = dec('8.33')
    max_len = 30
    def encode(self, s):
        l = int(len(s) * self.mag_num)
        res = [str(ord(c) * l) for c in s]
        return ''.join(res)[:self.max_len]
__all__.append('PD2')
encoder_classes['pd2'] = PD2


class PD3(object):
    '''
    A more advanced hasher based on PD2(). Should be suitable for passwords, 
    as well as checksums, especially as it is a new hasher. NOTE: This is slow!
    
    AUTHORS:
    v0.2.6+         --> pydsigner
    '''
    decimal.getcontext().prec = 15
    mag_num = dec(5 ** 2 + 9 ** 2).sqrt().rotate(6)
    max_len = 64
    def encode(self, s):
        l = int(dec(len(s)) * self.mag_num)
        res = [str(ord(c) * l) for c in s]
        # how slow will this make this hasher?
        decimal.getcontext().prec = 77
        d = dec(''.join(res)).rotate(-1)
        return sane_hex(d)[:self.max_len]
__all__.append('PD3')
encoder_classes['pd3'] = PD3


class PD4(object):
    '''
    A more advanced hasher based on PD3(). Should be suitable for passwords, 
    but you may wish to look at PD5(), PD7(), or PD8() for checksums. 
    NOTE: This is VERY slow!
    
    AUTHORS:
    v0.2.9+         --> pydsigner
    '''
    decimal.getcontext().prec = 15
    mag_num = dec(6 ** 2 + 1).sqrt().rotate(-9)
    max_len = 96
    def encode(self, s):
        l = int(dec(len(s)) * self.mag_num)
        res = ''.join([str(hash(c) * l) for c in s]).replace('-', '56')
        # Is speed going to be a problem here?
        decimal.getcontext().prec = 116
        d = dec(res).rotate(-2)
        return sane_hex(d)[:self.max_len]
__all__.append('PD4')
encoder_classes['pd4'] = PD4


class PD5(object):
    '''
    A hasher that is much faster than PD4(), but more suited for generating 
    checksums than password storage because of its limited length (23 - 30 
    characters)
    
    AUTHORS:
    v0.3.0+         --> pydsigner.
    '''
    max_len = 128
    mag_num = int(dec(40).exp())
    def encode(self, s):
        l = self.mag_num * len(s)
        r = int(str(hash(s) * l).replace('-', str(self.max_len)))
        return sane_hex(r)[:self.max_len]
__all__.append('PD5')
encoder_classes['pd5'] = PD5


class PD6(object):
    '''
    A hasher that is slower than PD5(), but better suited for password 
    storage and much faster than PD4(). WARNING: It is not recommended that one 
    use this hasher on strings more than 256 characters long.
    
    AUTHORS:
    v0.3.1+         --> pydsigner.
    '''
    max_len = 128
    mag_num = int(dec(46).exp())
    split_size = 2
    dash = mag_num // 3
    def encode(self,  s):
        z = len(s) // self.split_size
        z += 1 if len(s) % self.split_size else 0
        bitesize = self.max_len * 2 * self.split_size
        sec = pgpu.section(s[:bitesize], self.split_size)
        l = self.mag_num * z
        r = int(''.join([str(hash(s) * l).replace('-', str(self.dash)
                ) for s in sec]))
        return sane_hex(r)[:self.max_len]
__all__.append('PD6')
encoder_classes['pd6'] = PD6


class PD7(PD6):
    '''
    A fast checksum generator similar to, but slower than, the popular md5. 
    For a longer generator, see PD8(). WARNING: It is not recommended that one 
    use this hasher on strings more than 128 characters long.
    
    AUTHORS:
    v0.3.6+         --> pydsigner.
    '''
    max_len = 32
    mag_num = 68
    split_size = 4
    dash = mag_num // 5
__all__.append('PD7')
encoder_classes['pd7'] = PD7


class PD8(PD6):
    '''
    A checksum generator designed to be right between PD7() and PD6() in 
    terms of speed and quality. WARNING: It is not recommended that one use 
    this hasher on strings more than 192 characters long.
    
    AUTHORS:
    v0.3.4+         --> pydsigner.
    '''
    max_len = 64
    mag_num = 57
    split_size = 3
    dash = (mag_num * 6) // 19
__all__.append('PD8')
encoder_classes['pd8'] = PD8


class PD9(object):
    '''
    A hasher designed to replace PD6().
    
    AUTHORS:
    v0.3.5+         --> pydsigner.
    '''
    max_len = 128
    mag_num = int(dec(53).exp())
    split_size = 2
    dash = str((mag_num * 2) // 7)
    def encode(self, s):
        z = len(s) // self.split_size
        z += 1 if len(s) % self.split_size else 0
        bitesize = self.max_len * 2 * self.split_size
        sec = pgpu.section(s[:bitesize], self.split_size)
        l = self.mag_num * z
        v = ''.join([str(hash(s[bitesize:]))] + [str(hash(s) * l
                ).replace('-', self.dash) for s in sec])
        r = int(v) # int(str(hash(s[bitesize:])).replace('-', self.dash) + v)
        return sane_hex(r)[:self.max_len]
__all__.append('PD9')
encoder_classes['pd9'] = PD9


class PD10(PD9):
    '''
    A hasher designed to replace PD7().
    
    AUTHORS:
    v0.3.5+         --> pydsigner.
    '''
    max_len = 32
    mag_num = int(dec(57).exp())
    split_size = 4
    dash = str(mag_num // 4)
__all__.append('PD10')
encoder_classes['pd10'] = PD10


class PD11(PD9):
    '''
    A hasher designed to replace PD8().
    
    AUTHORS:
    v0.3.5+         --> pydsigner.
    '''
    max_len = 64
    mag_num = int(dec(43).exp()) * 9
    split_size = 3
    dash = str(int(dec(31).exp()))
__all__.append('PD11')
encoder_classes['pd11'] = PD11


class PD12(object):
    '''
    Similar to but not the same as PD9().
    
    AUTHORS:
    v0.3.6+         --> pydsigner.
    '''
    max_len = 128
    mag_num = 7
    split_size = 2
    dash = str(int(dec(23).exp()))
    def encode(self, s):
        z = len(s) // self.split_size
        z += 1 if len(s) % self.split_size else 0
        bitesize = self.max_len * 2 * self.split_size
        sec = pgpu.section(s[:bitesize], self.split_size)
        end = s[bitesize:]
        end36 = pgpu.keep_many(end, string.ascii_letters + string.digits)
        q = int(end36, 36) if end36 else 0
        ds = int(self.dash)
        if q < ds * 2 // 3 or not q or q < 0:
            q = ds
        l = self.mag_num * z * q
        v = ''.join([str(hash(end))] + [str(hash(s) * l
                ).replace('-', self.dash) for s in sec])
        r = int(v)
        return sane_hex(r)[:self.max_len]
__all__.append('PD12')
encoder_classes['pd12'] = PD12


class PD13(PD12):
    '''
    Similar to PD10() but based on PD12().
    
    AUTHORS:
    v0.3.6+         --> pydsigner.
    '''
    max_len = 32
    mag_num = 3
    split_size = 4
    dash = str(int(dec(13).exp()))
__all__.append('PD13')
encoder_classes['pd13'] = PD13


class PD14(PD12):
    '''
    Similar to PD11() but based on PD12().
    
    AUTHORS:
    v0.3.6+         --> pydsigner
    '''
    max_len = 64
    mag_num = 5
    split_size = 3
    dash = str(int(dec(17).exp()))
__all__.append('PD14')
encoder_classes['pd14'] = PD14


class RD(object):
    '''
    Seeds the random module with the object to be hashed; returns the str()ed 
    result of random.randint(self.small, self.big). Possible weaknesses: Does 
    random return the same numbers on all platforms? Will threading break 
    this?
    
    AUTHORS:
    v0.4.7+         --> pydsigner
    '''
    small = 0
    big = 10 ** 10
    def encode(self, s):
        random.seed(s)
        return str(random.randint(self.small, self.big))
__all__.append('RD')
encoder_classes['rd'] = RD


class SHA1(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return hashlib.sha1(s).hexdigest()
__all__.append('SHA1')
encoder_classes['sha1'] = SHA1


class SHA224(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return hashlib.sha224(s).hexdigest()
__all__.append('SHA224')
encoder_classes['sha224'] = SHA224


class SHA256(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return hashlib.sha256(s).hexdigest()
__all__.append('SHA256')
encoder_classes['sha256'] = SHA256


class SHA384(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return hashlib.sha384(s).hexdigest()
__all__.append('SHA384')
encoder_classes['sha384'] = SHA384


class SHA512(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return hashlib.sha512(s).hexdigest()
__all__.append('SHA512')
encoder_classes['sha512'] = SHA512


class MD5(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return hashlib.md5(s).hexdigest()
__all__.append('MD5')
encoder_classes['md5'] = MD5


class Base16(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return base64.b16encode(s)
    def decode(self, s):
        return base64.b16decode(s)
__all__.append('Base16')
encoder_classes['base16'] = Base16


class Base32(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return base64.b32encode(s)
    def decode(self, s):
        return base64.b32decode(s)
__all__.append('Base32')
encoder_classes['base32'] = Base32


class Base64(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return base64.b64encode(s)
    def decode(self, s):
        return base64.b64decode(s)
__all__.append('Base64')
encoder_classes['base64'] = Base64


class Hex(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return binascii.b2a_hex(s)
    def decode(self, s):
        return binascii.a2b_hex(s)
__all__.append('Hex')
encoder_classes['hex'] = Hex


class HQX(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return binascii.b2a_hqx(s)
    def decode(self, s):
        return binascii.a2b_hqx(s)[0]
__all__.append('HQX')
encoder_classes['hqx'] = HQX


class UU(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return binascii.b2a_uu(s)
    def decode(self, s):
        return binascii.a2b_uu(s)
__all__.append('UU')
encoder_classes['uu'] = UU


class URL(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    def encode(self, s):
        return urler.quote(s)
    def decode(self, s):
        return urler.unquote(s)
__all__.append('URL')
encoder_classes['url'] = URL


class HTML(object):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    conv_dict = {'<': '&#60;', '>': '&#62;', '"': '&#34;', '&': '&#38;'}
    def encode(self, s):
        return pgpu.replace_many(s, self.conv_dict)
    def decode(self, s):
        return pgpu.replace_many(s, self.conv_dict, True)
__all__.append('HTML')
encoder_classes['html'] = HTML


class CRC32(object):
    '''
    AUTHORS:
    v0.2.7+         --> pydsigner
    '''
    def encode(self, s):
        return zlib.crc32(s)
__all__.append('CRC32')
encoder_classes['crc32'] = CRC32


class Adler32(object):
    '''AUTHORS:
    v0.2.7+         --> pydsigner'''
    def encode(self, s):
        return zlib.adler32(s)
__all__.append('Adler32')
encoder_classes['adler32'] = Adler32


def fetcher(encoder):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    return encoder_classes[encoder.lower()]()


def rand_key(l = 10):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    res = ''
    while len(res) < l:
        v = str(math.log((random.randint(1, 33) * math.pi) ** 2))
        res += pgpu.remove_many(v, 'e-.')
    return res[:l]


def multi_pass(user, pswd, times=1000, hasher=SHA512()):
    '''
    AUTHORS:
    v0.2.0+         --> pydsigner
    '''
    for i in range(0, times):
        pswd = hasher.encode(pswd + user + str(i))
    return pswd
