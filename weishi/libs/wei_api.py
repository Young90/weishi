#coding:utf-8
__author__ = 'young'
# 微信的api，从微信服务器获取信息
import urllib2


ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'


def get_access_token(app_id, app_secret):
    return read_url(ACCESS_TOKEN_URL % (app_id, app_secret))


def read_url(url):
    """从url中读取信息"""
    print url
    request = urllib2.Request(url)
    response = urllib2.urlopen(request)
    return response.read()