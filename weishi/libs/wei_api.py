#coding:utf-8
__author__ = 'young'

import datetime
import json
from tornado.httpclient import AsyncHTTPClient
from tornado import gen


ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
FANS_LIST_URL = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s'
FANS_LIST_URL_CONTINUE = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s'


class WeiAPI(object):
    """
    微信接口访问类
    """
    a = None

    @gen.coroutine
    def get_access_token(self, account, callback):
        """获取access_token"""
        WeiAPI.a = account
        client = AsyncHTTPClient(max_clients=20)
        url = ACCESS_TOKEN_URL % (account.app_id, account.app_secret)
        response = yield gen.Task(client.fetch, url)
        body = json.loads(response.body)
        print body
        if body['access_token']:
            access_token = body['access_token']
            # 计算access_token过期时间，为了保证可用，比官方时间少200s
            time = datetime.datetime.now() + datetime.timedelta(seconds=7000)
            self.a.access_token = access_token
            self.a.expires = time
        if callback:
            callback(self.a)