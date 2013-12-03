#coding:utf-8
__author__ = 'young'

import hashlib
from zhuangxiutai.libs.const import Role

m = hashlib.md5()
m.update('123456' + Role.SALT)
print m.hexdigest()