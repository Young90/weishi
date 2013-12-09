#coding:utf-8
__author__ = 'young'

from tornado.web import HTTPError
from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
from weishi.libs.wei_api import get_access_token


class AccountBaseHandler(BaseHandler):
    """
    用户管理微信号的base handler
    """

    account = None

    @authenticated
    def prepare(self):
        aid = self.request.uri.split('/')[2]
        if not aid:
            raise HTTPError(404)
            return
        print aid
        account = self.db.get('select * from t_account where aid = %s', aid)
        if not account:
            raise HTTPError(404)
            return
        if account.user_id != self.current_user.id:
            raise HTTPError(403)
            return
        AccountBaseHandler.account = account

    def _get_access_token(self):
        """当access_token过期后，获取微信的access_token"""
        access_token = get_access_token(self.account.app_id, self.account.app_secret)
        if access_token['access_token']:
            self.db.execute('update t_account set access_token = %s and expires = %s', access_token['access_token'])


class AccountIndexHandler(AccountBaseHandler):
    """
    微信号管理的默认处理方法
    """

    def get(self, aid):
        self.render('account/index.html', account=self.account)


class AccountFansHandler(AccountBaseHandler):
    """
    获取微信账号的粉丝列表
    """

    def get(self, aid):
        account = self.account


handlers = [
    (r'/account/([^/]+)', AccountIndexHandler),
    (r'/account/([^/]+)/fans', AccountFansHandler),
]