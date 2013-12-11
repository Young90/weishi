#coding:utf-8
__author__ = 'young'

import datetime
from tornado.web import HTTPError, asynchronous
import tornado.gen
from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
from weishi.libs import wei_api


class AccountBaseHandler(BaseHandler):
    """
    用户管理微信号的base handler
    用户进入/account/{aid}/*的页面，保证获取的access_token可用
    """

    account = None

    @authenticated
    @asynchronous
    def prepare(self):
        aid = self.request.uri.split('/')[2]
        if not aid:
            raise HTTPError(404)
            return
        account = self.db.get('select * from t_account where aid = %s', aid)
        if not account:
            raise HTTPError(404)
            return
        if account.user_id != self.current_user.id:
            raise HTTPError(403)
            return
        if not account.expires or account.expires < datetime.datetime.now():
            wei_api.get_access_token(account, self._update_account_token)
        AccountBaseHandler.account = account

    def _update_account_token(self, account):
        """当access_token过期后，获取微信的access_token"""
        print 'account.py _update_account_token start...'
        self.account['access_token'] = account.access_token
        self.account['expires'] = account.expires
        self.db.execute('update t_account set access_token = %s, expires = %s where aid = %s',
                        self.account.access_token, self.account.expires, self.account.aid)
        print 'account.py _update_account_token end...'

    def _get_fans(self):
        """获取账号的所有粉丝"""
        return self.db.query('select * from t_fans where aid = %s', self.account.aid)


class AccountIndexHandler(AccountBaseHandler):
    """
    微信号管理的默认处理方法
    """

    def get(self, aid):
        print 'account.py index start...'
        self.render('account/index.html', account=self.account)
        print 'account.py index end...'


class AccountFansHandler(AccountBaseHandler):
    """
    查看公共账号的所有粉丝
    """

    @tornado.gen.coroutine
    def get(self, aid):
        print 'account.py fans_list start...'
        fans = self._get_fans()
        print 'account.py fans_list end...'
        self.render('account/index.html', fans=fans, account=self.account)


handlers = [
    (r'/account/([^/]+)', AccountIndexHandler),
    (r'/account/([^/]+)/fans', AccountFansHandler),
]