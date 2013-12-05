#coding:utf-8
__author__ = 'young'

import string
from weishi.libs.handler import BaseHandler
from weishi.libs.decorators import authenticated
from weishi.form.front_from import AccountForm
from weishi.libs.id_generator import id_gen
from weishi.libs.const import DOMAIN_NAME


class FrontBaseHandler(BaseHandler):
    # 保存微信账号
    def _create_account(self, app_id, app_name, app_account, token, aid):
        self.db.excute('insert into t_account (data, app_id, app_name, app_account, token, aid, user_id) '
                       'values (NOW(), %s, %s, %s, %s, %s)',
                       app_id, app_name, app_account, token, aid, self.current_user.id)

    # 从aid获取account
    def _get_account_by_aid(self, aid):
        return self.db.get('select * from t_account where aid = %s', aid)


class FrontIndexHandler(BaseHandler):
    """
    账号管理首页，显示所有的公众账号
    """

    @authenticated
    def get(self):
        user_id = self.current_user.id
        accounts = self.db.get('select * from t_account where user_id = %s', user_id)
        self.render("index.html", accounts=accounts)


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
        self.render("add_account.html")

    @authenticated
    def post(self, *args, **kwargs):
        account_form = AccountForm(self.request.arguments)
        if not account_form.validate():
            errors = account_form.errors
            error = ''.join(errors.values()[0][0])
            r = {"r": 0, "error": error}
            self.write(r)
            return
        app_id = account_form.data['app_id']
        app_name = account_form.data['app_name']
        app_account = account_form.data['app_account']
        aid = id_gen(9, string.ascii_lowercase)
        token = id_gen(6, string.digits)
        self._create_account(app_id, app_name, app_account, token, aid)
        account = self._get_account_by_aid(aid)

        while account:
            aid = id_gen(9, string.ascii_lowercase)
            account = self._get_account_by_aid(aid)

        r = {"r": 1, "token": token, "url": DOMAIN_NAME + "/api/" + aid}
        self.write(r)


handlers = [
    (r"/", FrontIndexHandler),
    (r"/accounts", AccountsHandler),
]
