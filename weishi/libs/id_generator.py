#coding:utf-8
__author__ = 'young'

import random


def id_gen(length, lib):
    return ''.join([random.choice(lib) for i in range(0, length)])