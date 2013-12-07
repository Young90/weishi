#coding:utf-8
__author__ = 'young'

import urllib
import urllib2
import hashlib
import xmltodict
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
url = 'http://127.0.0.1:8888/signup'
values = {
    'username': '侯西阳',
    'email': '123456@cc.cc',
    'password': '123457',
    'mobile': '13524712918',
}

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
print response.read()
"""
tmp_list = {'r': 0}

print tmp_list
"""
"""
xml = '<xml>' \
      '<ToUserName><![CDATA[toUser]]></ToUserName>' \
      '<FromUserName><![CDATA[fromUser]]></FromUserName>' \
      '<CreateTime>1348831860</CreateTime>' \
      '<MsgType><![CDATA[text]]></MsgType>' \
      '<Content><![CDATA[this is a test]]></Content>' \
      '<MsgId>1234567890123456</MsgId>' \
      '</xml>'

message = xmltodict.parse(xml)['xml']

print message['MsgType']
"""