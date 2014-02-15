#coding:utf-8
__author__ = 'young'

import random


def generate_hexdigits_lower(length):
    """从hex数中产生字符串"""
    hexdigits = '0123456789abcdef'
    return ''.join([random.choice(hexdigits) for i in range(0, length)])


def generate_digits_starts_with(starts, length):
    """产生纯数字字符串，并以某几个字符开头"""
    digits = '0123456789'
    return starts + ''.join([random.choice(digits) for i in range(0, length - len(starts))])

