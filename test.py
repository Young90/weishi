#coding:utf-8
__author__ = 'young'

import urllib
import urllib2
import hashlib
from weishi.libs.const import DOMAIN_NAME

"""
m = hashlib.md5()
m.update('123456' + 'SSSS')
print m.hexdigest()

url = 'http://127.0.0.1:8888/login'
values = {
    'user': '侯西阳',
    'email': '123456@cc.cc',
    'password': '123457'
}

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
print response.read()
"""
"""
url = 'http://127.0.0.1:8888/signup'
values = {
    'username': '侯西阳',
    'email': '123456@cc',
    'password': '123457',
    'mobile': '13524712918',
}

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
print response.read()
"""

tmp_list = ['123', '侯西阳', 'bhf', 'ilhil']
tmp_list.sort()
print tmp_list
print ''.join(tmp_list)
print hashlib.sha1(''.join(tmp_list)).hexdigest()