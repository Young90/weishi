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
"""
import urllib2
import urllib

url = 'http://127.0.0.1:8888/account/oqdWRpYOP/message/fans/1'
values = {
    'content': '你好世界！',
    'fans_id': 1,
}

opener = urllib2.build_opener()
data = urllib.urlencode(values)
req = urllib2.Request(url, data=data,
                      headers={
                          'Cookie': 'user="MTIzNA==|1387196454|e25533fc4066848b2c6396569ba0f9c86f5a20b3"'
                      })
response = urllib2.urlopen(req)
print response.read()
"""
"""
import time
from weishi.libs import dicttoxml

response = {'ToUserName': 'toUser', 'FromUserName': 'developer', 'CreateTime': int(time.time()), 'Articles': [{}, {}],
            'MsgType': 'text', 'Content': u'欢迎关注'}

print dicttoxml.dicttoxml(response, root='xml')
print isinstance(u'侯西阳', basestring)
"""

result = {"button": [
    {
        "type": "click",
        "name": "今日歌曲",
        "key": "V1001_TODAY_MUSIC"
    },
    {
        "type": "click",
        "name": "歌手简介",
        "key": "V1001_TODAY_SINGER"
    },
    {
        "name": "菜单",
        "sub_button": [
            {
                "type": "view",
                "name": "搜索",
                "url": "http://www.soso.com/"
            },
            {
                "type": "view",
                "name": "视频",
                "url": "http://v.qq.com/"
            },
            {
                "type": "click",
                "name": "赞一下我们",
                "key": "V1001_GOOD"
            }]
    }]
}

print result