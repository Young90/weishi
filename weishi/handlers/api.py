#coding:utf-8
__author__ = 'young'

import hashlib
from weishi.libs.handler import BaseHandler


class APIBaseHandler(BaseHandler):
    def _get_account_by_aid(self, aid):
        return self.db.get('select * from t_account where aid = %s', aid)


class APIHandler(APIBaseHandler):
    """
    跟微信服务器通信的API
    GET：
        验证url跟token
    """

    def get(self, aid):
        print aid
        account = self._get_account_by_aid(aid)
        if not account:
            self.write('invalid account id')
            return
        signature = self.get_argument('signature', '')
        timestamp = self.get_argument('timestamp', '')
        nonce = self.get_argument('nonce', '')
        echostr = self.get_argument('echostr', '')
        token = account.token
        tmp_list = [token, timestamp, nonce]
        tmp_list.sort()
        if hashlib.sha1(''.join(tmp_list)).hexdigest() == signature:
            self.write(echostr)
            return
        self.write('invalid signature')
        return


handlers = [
    (r'/api/([^/]+)', APIHandler)
]