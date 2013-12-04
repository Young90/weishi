#coding:utf-8
__author__ = 'young'

import random
import string


lib = string.hexdigits

print ''.join(random.choice(lib) for i in range(0, 9))