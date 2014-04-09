#coding:utf-8
__author__ = 'young'

import hashlib

import xmltodict
from tornado.web import HTTPError
from weishi.libs.handler import BaseHandler
from weishi.libs import wei_api
from weishi.libs import message as message_util
from weishi.libs.service import AccountManager, FansManager


class APIBaseHandler(BaseHandler):
    """
    与微信服务器通讯的base handler
    """

    account_manager = None
    fans_manager = None
    article_manager = None

    def prepare(self):
        self.account_manager = AccountManager(self.db)
        self.fans_manager = FansManager(self.db)

    def _validate_signature(self, token, signature, timestamp, nonce):
        """
        校验消息的真实性
        """
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        print '_validate_signature ---------- %s' % tmp_list
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
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        echostr = self.get_argument('echostr', '')
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        if self._validate_signature(account.token, signature, timestamp, nonce):
            self.account_manager.check_account(aid)
            self.write(echostr)
            return
        self.write('invalid signature')

    def _validate_signature(self, token, signature, timestamp, nonce):
        """
        校验消息的真实性
        """
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        if hashlib.sha1(''.join(tmp_list)).hexdigest() == signature:
            return True
        return False

    def post(self, aid, *args, **kwargs):
        """POST请求为微信服务器针对用户操作做出的响应"""
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        if not wei_api.access_token_available(account):
            wei_api.get_access_token(account, self.account_manager.update_account_token)
        message = self._get_message()
        if not message:
            raise HTTPError(404)
        result = message_util.process_message(account, message, self.get_template_path())
        if result:
            self.write(result)


handlers = [
    (r'/api/([^/]+)', APIHandler)
]