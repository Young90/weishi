#coding:utf-8
__author__ = 'young'

import datetime
import json
import simplejson
from tornado.httpclient import AsyncHTTPClient
from tornado import gen


ACCESS_TOKEN_URL = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s'
FANS_LIST_URL = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s'
FANS_LIST_URL_CONTINUE = 'https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid=%s'
FANS_INFO_URL = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token=%s&openid=%s'
SEND_MESSAGE = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s'


def access_token_available(account):
    """验证access_token是否可用"""
    if not account.access_token:
        return False
    if not account.expires:
        return False
    if datetime.datetime.now() > account.expires:
        return False
    return True


@gen.coroutine
def get_access_token(account, callback, *args):
    """如果access_token过期或为空则获取access_token"""
    print 'wei_api.py get_access_token start...'
    client = AsyncHTTPClient(max_clients=20)
    url = ACCESS_TOKEN_URL % (account.app_id, account.app_secret)
    response = yield gen.Task(client.fetch, url)
    body = json.loads(response.body)
    try:
        if body['access_token']:
            access_token = body['access_token']
            # 计算access_token过期时间，为了保证可用，比官方时间少200s
            time = datetime.datetime.now() + datetime.timedelta(seconds=7000)
            account['access_token'] = access_token
            account['expires'] = time
    except KeyError:
        print body
    print 'wei_api.py get_access_token end...'
    if callback:
        callback(account, *args)


@gen.coroutine
def sync_fans_list(account, *callback):
    """同步账号的粉丝列表"""
    print 'wei_api.py sync_fans_list start...'
    client = AsyncHTTPClient(max_clients=20)
    url = FANS_LIST_URL % account.access_token
    response = yield gen.Task(client.fetch, url)
    body = json.loads(response.body)
    try:
        total = body['total']
        if total > 0:
            ids = body['data']['openid']
        if total > 10000:
            while 1:
                try:
                    next_openid = body['next_openid']
                    url = FANS_LIST_URL_CONTINUE % (account.access_token, next_openid)
                    response = yield gen.Task(client.fetch, url)
                    body = json.loads(response.body)
                    ids = ids.extend(body['data']['openid'])
                except KeyError:
                    break
            print ids
    except KeyError:
        print body
    if ids:
        users = []
        for openid in ids:
            url = FANS_INFO_URL % (account.access_token, openid)
            response = yield gen.Task(client.fetch, url)
            body = json.loads(response.body)
            try:
                subscribe = body['subscribe']
                if not subscribe:
                    continue
                else:
                    users.append(body)
            except KeyError:
                continue
    print 'wei_api.py sync_fans_list end...'
    if callback:
        method = callback[0]
        method(users, account.aid)


@gen.coroutine
def get_user_info(account, openid, *callback):
    """获取用户信息"""
    print 'wei_api.py get_user_info start...'
    client = AsyncHTTPClient(max_clients=20)
    url = FANS_INFO_URL % (account.access_token, openid)
    response = yield gen.Task(client.fetch, url)
    body = json.loads(response.body)
    try:
        subscribe = body['subscribe']
        if subscribe:
            user = body
    except KeyError:
        print body
    print 'wei_api.py get_user_info end...'
    if callback:
        method = callback[0]
        method(user, account.aid)


@gen.coroutine
def send_text_message(account, message, *callback):
    """发送文字消息"""
    print "send text message : %s" % simplejson.dumps(message)
    client = AsyncHTTPClient(max_clients=20)
    url = SEND_MESSAGE % account.access_token
    response = yield gen.Task(client.fetch, url, method='POST',
                              body=simplejson.dumps(message, encoding='utf-8', ensure_ascii=False))
    print 'response : %s' % response
    body = json.loads(response.body)
    print 'body : %s' % body
    result = {'r': 1}
    try:
        errcode = body['errcode']
        if errcode:
            print body
            result['error'] = '发送失败'
            result['r'] = 0
    except KeyError:
        print body
    if callback:
        method = callback[0]
        method(result)