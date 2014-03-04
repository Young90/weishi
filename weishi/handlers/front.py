#coding:utf-8
__author__ = 'young'

import string
from weishi.libs.handler import BaseHandler
from weishi.libs.decorators import authenticated
from weishi.form.front_from import AccountForm
from weishi.libs.image import upload
from weishi.libs.const import Image
from weishi.libs.service import AccountManager
from weishi.libs import key_util


class FrontBaseHandler(BaseHandler):
    account_manager = None

    def prepare(self):
        self.account_manager = AccountManager(self.db)


class FrontIndexHandler(BaseHandler):
    """
    账号管理首页，显示所有的公众账号
    """

    @authenticated
    def get(self):
        user_id = self.current_user.id
        accounts = self.db.query('select * from t_account where user_id = %s', user_id)
        self.render('index.html', accounts=accounts)


class AccountsHandler(FrontBaseHandler):
    """
    添加微信管理账号
    GET:
        返回对应页面
    POST：
        提交添加账号的数据
    """

    @authenticated
    def get(self):
        self.render('add_account.html', user=self.get_current_user())

    @authenticated
    def post(self, *args, **kwargs):
        f = AccountForm(self.request.arguments)
        if not f.validate():
            errors = f.errors
            error = ''.join(errors.values()[0][0])
            r = {'r': 0, 'error': error}
            self.write(r)
            return
        try:
            if self.request.files['avatar']:
                file_body = self.request.files['avatar'][0]['body']
                url = upload(file_body, Image.FOLDER_AVATAR)
        except KeyError:
            url = None
        print url
        aid = key_util.generate_hexdigits_lower(8)
        token = key_util.generate_hexdigits_lower(8)
        account = self.account_manager.get_account_by_aid(aid)

        while account:
            aid = key_util(8, string.hexdigits)
            account = self.account_manager.get_account_by_aid(aid)

        self.account_manager.create_account(f.data['wei_id'], f.data['wei_name'], f.data['wei_account'], token, aid,
                                            url, self.current_user.id)

        r = {'r': 1, 'aid': aid}
        self.write(r)

    @authenticated
    def delete(self, *args, **kwargs):
        """删除已经绑定的微信账号"""
        aid = self.get_argument('aid', '')
        account = self.account_manager.get_account_by_aid(aid)
        r = {'r': 0}
        if not account:
            r['error'] = '要删除的账号不存在！'
            self.write(r)
            return
        if account.user_id != self.current_user.id:
            r['error'] = '没有权限操作！'
            self.write(r)
            return
        self.account_manager.delete_account(aid, self.current_user.id)
        r['r'] = 1
        self.write(r)


class UpdateAppHandler(FrontBaseHandler):
    """
    更新账号的app信息
    """

    @authenticated
    def post(self, *args, **kwargs):
        """更新账号的app_id和app_secret"""
        aid = self.get_cookie('aid', '')
        app_id = self.get_argument('app_id', '')
        app_secret = self.get_argument('app_secret', '')
        account = self.account_manager.get_account_by_aid(aid)
        if not account or account.user_id != self.current_user.id:
            result = {'r': 0, 'error': '账号错误'}
            self.write(result)
        self.account_manager.update_account_app_info(aid, app_id, app_secret)
        result = {'r': 1}
        self.write(result)


handlers = [
    (r'/', FrontIndexHandler),
    (r'/accounts', AccountsHandler),
    (r'/accounts/update', UpdateAppHandler),
]
