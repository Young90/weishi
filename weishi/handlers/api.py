#coding:utf-8
__author__ = 'young'

import hashlib
import xmltodict
from tornado.web import HTTPError

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
            self.db.execute('insert into t_fans (date, openid, nickname, sex, country, province, '
                            'city, avatar, subscribe_time, aid) values (NOW(), %s, %s, %s, %s, %s, %s, '
                            '%s, %s, %s)', user['openid'], user['nickname'], user['sex'],
                            user['country'], user['province'], user['city'],
                            user['headimgurl'], user['subscribe_time'], aid)
        print 'apy.py _add_fans end...'

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
        if self._validate_signature(account):
            self._check_account(aid)
            wei_api.get_access_token(account, wei_api.sync_fans_list, self._add_fans)
            print 'api.py get end...'
            self.write(echostr)
            return
        self.write('invalid signature')

    def post(self, aid, *args, **kwargs):
        """POST请求为微信服务器针对用户操作做出的响应"""
        # TODO 后续需要完善各种信息类型的处理
        account = self._get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        message = self._get_message()
        print message
        if not message:
            raise HTTPError(404)


handlers = [
    (r'/api/([^/]+)', APIHandler)
]