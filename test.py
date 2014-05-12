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

print str(result)
"""
"""
import urllib
import urllib2

xml = '<xml><ToUserName><![CDATA[程序员]]></ToUserName><FromUserName><![CDATA[123456456]]></FromUserName>' \
      '<CreateTime>1348831860</CreateTime><MsgType><![CDATA[event]]></MsgType><Event><![CDATA[subscribe]]></Event></xml>'

url = 'http://127.0.0.1:8888/api/oqdWRpYOP'

req = urllib2.Request(url, xml)
response = urllib2.urlopen(req)
print response.read()
"""
"""
import hashlib

password = '900717'

m = hashlib.md5()
m.update(password + 'this is salt')
p = m.hexdigest()

print p
"""
"""
id_list = [1, 2, 3, 0, 0, 0]

id_list = filter(lambda a: a != 0, id_list)

print ','.join(str(x) for x in id_list)
"""
"""
import hashlib

tmp_list = ['68b20b98', '1393770355', '1394248361']
tmp_list.sort()
print '_validate_signature ---------- %s' % tmp_list
print hashlib.sha1(''.join(tmp_list)).hexdigest()
"""
"""
a = 10
b = '号码'
print str(a) + b
"""
"""
import time
from dateutil import parser
t = 'Fri May 02 2014 23:00:03 GMT+0800'
dt = parser.parse(t)
timestamp = time.mktime(dt.timetuple())
print int(timestamp)
"""
"""
import datetime
import time
ltime=time.localtime(1402066810.0)
print ltime
"""
import urllib2
from BeautifulSoup import BeautifulSoup

cookie = 'wosid=QWmC8WT7WjJS6ncDk0ewG0; woinst=3313; dssid2=208c3beb-08d9-4b51-938c-00f6ef4f9b86; optimizelyEndUserId=oeu1397007086465r0.5295939857605845; pxro=2; accs=o; dslang=US-EN; POD=cn~zh; ds01_a=e31d0d9f697bf940a1c997f5bac0f0cbfec62a9727e80da8f67d5a06e5620030ca04e4ba4224c275e5f944758b9e08b2706a134fc19f585cb27e0af431ed6e218437a6af024130fc50b0f780db64a53faee4cb82732425047dc3ed2bf8e23d8eGZVX; ac_recentproducts=PP460%3AFinal%20Cut%20Pro%20X%20%2810.1%29%20-%20User%20Guide; ccl=g+KsiKVbO2RGjPiY8bkeBQ==; geo=CN; myacinfo=DAWTKNV2d8a13602b1664bb581a9ed198842a48080e7d944ebf68f83d9a53740c2aa07911b478906a31344759efedc19a58f6b59f794d054298e964e7202b267c18644122f61df762dfd29beaf109fd61de341fc65a44234937cbe77be86c0c45a7cd4ff910ae049f8eb2b8e1aae75ae06f801bd5488203edf61895b8682b2f48d2161313501d6438fcd0f906ce9f997da3eda5c11340e82fdcc28676b42030948ad46971a627c417ce1a4cec84e8e3ffabe9977cb6fd38b59e55b58505b11c298acbc6f81278c429e2ed77441ccb30a0ab46bbe7cf1a6bc533f210d1769949d17d14d53b572059100db872c172c318a486ee4f76be123529fd90d0de4b62db4b2174c0da41603044a835689c39530450f166d93b36add421c3e2ddfa39cab7ae053b738d00cfb05c01bd9eac96bd051bc3b89b0MVRYV2; ds01=A29B7BA57B70801BDC2E0F3C00A4DA168BC3C5E155B941141F286F3BC06DD84DF0CD27934B47B42BE51D346953899F58B0AFB0803BCD287571400E548000BD63; s_vnum_n2_us=4|10,3|3,0|2,19|16,26|1; s_vnum_n2_cn=0%7C9%2C3%7C6%2C26%7C2%2C31%7C1%2C63%7C1%2C1%7C1%2C19%7C1; optimizelySegments=%7B%22341793217%22%3A%22referral%22%2C%22341794206%22%3A%22false%22%2C%22341824156%22%3A%22gc%22%2C%22341932127%22%3A%22none%22%2C%22381100110%22%3A%22gc%22%2C%22381740105%22%3A%22none%22%2C%22382310071%22%3A%22referral%22%2C%22382310072%22%3A%22false%22%7D; optimizelyBuckets=%7B%22698469559%22%3A%22696726683%22%7D; s_fid=4DDD1043194AA779-3FA711638DB6C0A2; s_ppv=AOS%253A%2520Product%2520Details%2520-%2520Apple%25205W%2520USB%2520%25u7535%25u6E90%25u9002%25u914D%25u5668%2C49%2C32%2C1428%2C; s_cc=true; s_sq=%5B%5BB%5D%5D; s_vi=[CS]v1|299DF90905161AA0-400001832002FA78[CE]'
url = 'https://itunesconnect.apple.com/WebObjects/iTunesConnect.woa/wo/86.0.0.11.5.0.7.3.3.1.0.13.3.1.1.11.9.1.1.7.0'

opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', cookie))
f = opener.open(url).read()
soup = BeautifulSoup(f)
head = soup.find('span', {'class': 'metadataField metadataFieldReadonly'})
print 'Review' in str(head)