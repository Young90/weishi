#coding:utf-8
__author__ = 'young'

import string
from weishi.libs.handler import BaseHandler
from weishi.libs.decorators import authenticated
from weishi.form.front_from import AccountForm
from weishi.libs.id_generator import id_gen
from weishi.libs.const import DOMAIN_NAME


class FrontBaseHandler(BaseHandler):
    def _create_account(self, wei_id, wei_name, wei_account, app_id, app_secret, token, aid):
        """创建微信账号记录"""
        self.db.excute('insert into t_account (data, wei_id, wei_name, wei_account, app_id, app_secret,'
                       ' token, aid, user_id) values (NOW(), %s, %s, %s, %s, %s, %s, %s)',
                       wei_id, wei_name, wei_account, app_id, app_secret, token, aid, self.current_user.id)

    def _delete_account(self, aid, user_id):
        """删除账号记录"""
        self.db.excute('delete from t_account where aid = %s and user_id = %s', aid, user_id)

    def _get_account_by_aid(self, aid):
        """根据aid获取账号记录"""
        return self.db.get('select * from t_account where aid = %s', aid)


class FrontIndexHandler(BaseHandler):
    """
    账号管理首页，显示所有的公众账号
    """

    @authenticated
    def get(self):
        user_id = self.current_user.id
        accounts = self.db.get('select * from t_account where user_id = %s', user_id)
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
        self.render('add_account.html')

    @authenticated
    def post(self, *args, **kwargs):
        f = AccountForm(self.request.arguments)
        if not f.validate():
            errors = f.errors
            error = ''.join(errors.values()[0][0])
            r = {'r': 0, 'error': error}
            self.write(r)
            return
        aid = id_gen(9, string.ascii_lowercase)
        token = id_gen(6, string.digits)
        self._create_account(f.data['wei_id'], f.data['wei_name'], f.data['wei_account'],
                             f.data['app_id'], f.data['app_secret'], token, aid)
        account = self._get_account_by_aid(aid)

        while account:
            aid = id_gen(9, string.ascii_lowercase)
            account = self._get_account_by_aid(aid)

        r = {'r': 1, 'token': token, 'url': DOMAIN_NAME + '/api/' + aid}
        self.write(r)

    @authenticated
    def delete(self, *args, **kwargs):
        """删除已经绑定的微信账号"""
        aid = self.get_argument('aid', '')
        account = self._get_account_by_aid(aid)
        r = {'r': 0}
        if not account:
            r['error'] = '要删除的账号不存在！'
            self.write(r)
            return
        if account.user_id != self.current_user.id:
            r['error'] = '没有权限操作！'
            self.write(r)
            return
        self._delete_account(aid, self.current_user.id)
        r['r'] = 1
        self.write(r)


handlers = [
    (r'/', FrontIndexHandler),
    (r'/accounts', AccountsHandler),
]
