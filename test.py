#coding:utf-8
__author__ = 'young'

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
    'email': '123456@cc.cc',
    'password': '123457',
    'mobile': '13524712918',
}

data = urllib.urlencode(values)
req = urllib2.Request(url, data)
response = urllib2.urlopen(req)
print response.read()
"""
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
"""
from weishi.libs.wei_api import get_access_token

print get_access_token('wxd9b153fd2a25e52f', 'c430cc9ae3891ba936750c320a0789fd')
"""
"""
import datetime

now = datetime.datetime.now()
print now < now + datetime.timedelta(seconds=1000)
"""
"""
import math

print int(math.ceil(10 / 3))
"""
"""
import datetime

print datetime.datetime.fromtimestamp(int(1386764219))
"""
"""
from weishi.libs import wei_api


def _callback(result):
    print result


account = 'qAgMwCZHKTzqADChc_8a8p5_eb5gIXY3GWkRedNy3gHtkOR21IKetLovl67VSg7YAiiWfpE2RfUHx1YsiABchBYjmbGOsupUVOz_tQ1yLrj9HuvHyqBpZ8YHfrJw7Dema-_4J9fOjfBOJXJzz0XpWg'

message = {'msgtype': 'text', 'touser': 'ovuOEjhEt6UD6B4XvT3kxvC3WjGA', 'text': {'content': 'hello wei xin'}}
wei_api.send_text_message(account, message, _callback)
"""
import urllib2
import urllib

url = 'http://127.0.0.1:8888/account/oqdWRpYOP/message/fans/10'
values = {
    'content': '你好世界！',
    'fans_id': 1,
}

opener = urllib2.build_opener()
data = urllib.urlencode(values)
req = urllib2.Request(url, data=data,
                      headers={
                          'Cookie': 'user="MTIzNA==|1386677023|3ecb3ce6858a02fb7500a42e4e454ce127063922"'
                      })
response = urllib2.urlopen(req)
print response.read()