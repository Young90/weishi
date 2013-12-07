#coding:utf-8
__author__ = 'young'

import hashlib
import xmltodict

from tornado.web import HTTPError

from weishi.libs.handler import BaseHandler


class APIBaseHandler(BaseHandler):
    """
    与微信服务器通讯的base handler
    """

    def _get_account_by_aid(self, aid):
        """
        根据url中的aid获取account
        """
        return self.db.get('select * from t_account where aid = %s', aid)

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
        account = self._get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        echostr = self.get_argument('echostr', None)
        if self._validate_signature(account):
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