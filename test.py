#coding:utf-8
__author__ = 'young'

import urllib
import urllib2

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
url = 'http://127.0.0.1:8888/api/Xsajk4Ml'
values = '<xml>' \
         '<ToUserName><![CDATA[toUser]]></ToUserName>' \
         '<FromUserName><![CDATA[fromUser]]></FromUserName>' \
         '<CreateTime>1348831860</CreateTime>' \
         '<MsgType><![CDATA[text]]></MsgType>' \
         '<Content><![CDATA[this is a test]]></Content>' \
         '<MsgId>1234567890123456</MsgId>' \
         '</xml>'

req = urllib2.Request(url, data=values, headers={'Content-Type': 'application/xml'})
response = urllib2.urlopen(req)
print response.code()
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

message = xmltodict.parse(xml)['aa']

print message['MsgType']
"""