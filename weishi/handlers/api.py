#coding:utf-8
__author__ = 'young'

import hashlib
import datetime
import time

import xmltodict
from tornado.web import HTTPError
from tornado.template import Loader
from weishi.libs.handler import BaseHandler
from weishi.libs import wei_api


class APIBaseHandler(BaseHandler):
    """
    与微信服务器通讯的base handler
    """

    def _get_account_by_aid(self, aid):
        """
        根据url中的aid获取account
        """
        return self.db.get('select * from t_account where aid = %s', aid)

    def _check_account(self, aid):
        """经过微信服务器验证的，将checked设为1"""
        self.db.execute('update t_account set checked = 1 where aid = %s', aid)

    def _add_fans(self, users, aid):
        """将粉丝插入数据库"""
        print 'apy.py _add_fans start...'
        for user in users:
            print user
            self._add_single_fan(user, aid)
        print 'apy.py _add_fans end...'

    def _add_single_fan(self, user, aid):
        """添加单个粉丝用户信息"""
        self.db.execute('insert into t_fans (date, openid, nickname, sex, country, province, city, avatar, '
                        'subscribe_time, language, aid) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        user['openid'], user['nickname'], user['sex'], user['country'], user['province'],
                        user['city'], user['headimgurl'], datetime.datetime.fromtimestamp(int(user['subscribe_time'])),
                        user['language'], aid)

    def _remove_fans(self, openid):
        """取消关注，移除粉丝"""
        self.db.execute('delete from t_fans where openid = %s', openid)

    def _validate_signature(self, account):
        """
        校验消息的真实性
        """
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        token = account.token
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        if hashlib.sha1(''.join(tmp_list)).hexdigest() == signature:
            return True
        return False

    def _get_message(self):
        """将微信服务器POST过来xml格式的消息转换成dict"""
        try:
            message = xmltodict.parse(self.request.body)['xml']
            return message
        except KeyError:
            return None

    def _update_account_token(self, account):
        """需要access_token的操作，获取access_token后保存"""
        self.db.execute('update t_account set access_token = %s, expires = %s',
                        account.access_token, account.expires)

    def _get_auto_response(self, account):
        """获取公众账号设置的自动回复消息"""
        return self.db.get('select * from t_article where aid = %s and auto_response = 1', account.aid)


class APIHandler(APIBaseHandler):
    """
    跟微信服务器通信的API
    GET：
        验证url跟token
    """

    def get(self, aid):
        """GET请求为微信服务器验证url和token的准确性"""
        print 'api.py get start...'
        account = self._get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        echostr = self.get_argument('echostr', '')
        if not self._validate_signature(account):
            self._check_account(aid)
            wei_api.get_access_token(account, wei_api.sync_fans_list, self._add_fans)
            print 'api.py get end...'
            self.write(echostr)
            return
        self.write('invalid signature')

    def post(self, aid, *args, **kwargs):
        """POST请求为微信服务器针对用户操作做出的响应"""
        account = self._get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        if not wei_api.access_token_available(account):
            wei_api.get_access_token(account, self._update_account_token)
        message = self._get_message()
        if not message:
            raise HTTPError(404)
        print message
        if message['MsgType'] == 'event' and message['event'] == 'subscribe':
            """用户关注该账号"""
            openid = message['FromUserName']
            print openid
            wei_api.get_user_info(account, openid, self._add_single_fan)
            result = self._subscribe_response(account, openid)
            if result:
                self.set_header('Content-type', 'text/xml')
                self.write(result)
            return
        if message['MsgType'] == 'event' and message['event'] == 'unsubscribe':
            """用户取消关注账号"""
            openid = message['FromUserName']
            print openid
            self._remove_fans(openid)
            return

    def _subscribe_response(self, account, openid):
        """获取设置的自动回复消息"""
        article = self._get_auto_response(account)
        if not article:
            return None
        result = {'ToUserName': openid, 'FromUserName': account.weishi_account, 'CreateTime': int(time.time())}
        if article.type == 'text':
            result['MsgType'] = 'text'
            result['Content'] = article.content
            return Loader(self.get_template_path()).load('message/text_message.xml').generate(result=result)
        else:
            # TODO 完善图文消息的发送
            return None
        return None


handlers = [
    (r'/api/([^/]+)', APIHandler)
]