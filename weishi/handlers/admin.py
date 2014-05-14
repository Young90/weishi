#coding:utf-8
__author__ = 'young'

from weishi.libs.handler import BaseHandler
from weishi.libs.decorators import admin
from weishi.libs.service import UserManager, AccountManager


class AdminBaseHandler(BaseHandler):
    user_manager = None
    account_manager = None

    @admin
    def prepare(self):
        self.user_manager = UserManager(self.db)
        self.account_manager = AccountManager(self.db)


class IndexHandler(AdminBaseHandler):
    """管理后台首页"""

    def get(self):
        users = self.user_manager.list_users(0, 100)
        self.render('admin/index.html', index='users', users=users)


class NewUserHandler(AdminBaseHandler):
    """新添加用户"""

    def get(self):
        self.render('admin/new_user.html', index='new_user')

    def post(self, *args, **kwargs):
        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        phone = self.get_argument('phone', None)
        password = self.get_argument('password', None)
        if not username or not email or not password:
            result = {'r': 0, 'error': '参数不完整'}
            self.write(result)
            return
        self.user_manager.create_user(username, email, password, phone, '')
        result = {'r': 1}
        self.write(result)


class AccountHandler(AdminBaseHandler):
    """管理后台微信公众号管理页面"""

    def get(self):
        accounts = self.account_manager.list_accounts(0, 100)
        self.render('admin/accounts.html', index='accounts', accounts=accounts)

    def post(self, *args, **kwargs):
        user_id = self.get_argument('user_id', 0)
        account_id = self.get_argument('account_id', 0)
        if not user_id or not account_id:
            result = {'r': 0, 'error': '输入的参数不正确'}
            self.write(result)
            return
        user = self.user_manager.get_user_by_id(user_id)
        if not user:
            result = {'r': 0, 'error': '用户不存在'}
            self.write(result)
            return
        account = self.account_manager.get_account_by_id(account_id)
        if not account:
            result = {'r': 0, 'error': '微信账号不存在'}
            self.write(result)
            return
        self.account_manager.change_account_user(account.aid, user_id)
        result = {'r': 1}
        self.write(result)
        return


class AuthHandler(AdminBaseHandler):
    """修改账号权限"""

    def post(self, *args, **kwargs):
        _id = self.get_argument('id', 0)
        form = self.get_argument('form', 0)
        menu = self.get_argument('menu', 0)
        card = self.get_argument('card', 0)
        site = self.get_argument('site', 0)
        impact = self.get_argument('impact', 0)
        event = self.get_argument('event', 0)
        self.account_manager.change_auth(int(_id), int(menu), int(card), int(form), int(site), int(impact), int(event))
        self.write({'r': 1})
        return


handlers = [
    (r'/admin', IndexHandler),
    (r'/admin/accounts', AccountHandler),
    (r'/admin/new_user', NewUserHandler),
    (r'/admin/auth', AuthHandler)
]