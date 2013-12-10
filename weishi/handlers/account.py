#coding:utf-8
__author__ = 'young'

import json
import datetime
from tornado.web import HTTPError, asynchronous
import tornado.gen
from tornado.httpclient import AsyncHTTPClient
from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
from weishi.libs.wei_api import ACCESS_TOKEN_URL, FANS_LIST_URL


class AccountBaseHandler(BaseHandler):
    """
    用户管理微信号的base handler
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
            url = ACCESS_TOKEN_URL % (account.app_id, account.app_secret)
            client = AsyncHTTPClient()
            client.fetch(url, self._get_access_token)
        AccountBaseHandler.account = account

    def _get_access_token(self, response):
        """当access_token过期后，获取微信的access_token"""
        body = json.loads(response.body)
        if body['access_token']:
            access_token = body['access_token']
            time = datetime.datetime.now() + datetime.timedelta(seconds=7000)
            self.account.access_token = access_token
            self.account.expires = time
            self.db.execute('update t_account set access_token = %s, expires = %s where aid = %s',
                            access_token, time, self.account.aid)
        else:
            raise HTTPError(404)
        self.finish()


class AccountIndexHandler(AccountBaseHandler):
    """
    微信号管理的默认处理方法
    """

    def get(self, aid):
        self.render('account/index.html', account=self.account)


class AccountFansHandler(AccountBaseHandler):
    """
    异步从微信服务器获取粉丝数量
    显示已经同步的列表
    """

    @tornado.gen.coroutine
    def get(self, aid):
        access_token = self.account.access_token
        url = FANS_LIST_URL % access_token
        client = AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch, url)
        body = json.loads(response.body)
        print body
        try:
            total = body['total']
        except KeyError:
            total = 0
        self.write(str(total))
        self.finish()


handlers = [
    (r'/account/([^/]+)', AccountIndexHandler),
    (r'/account/([^/]+)/fans', AccountFansHandler),
]