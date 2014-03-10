#coding:utf-8
__author__ = 'young'

from weishi.libs.handler import BaseHandler
from weishi.libs.const import EMAIL_REGEX
from weishi.form.user_form import SignupForm
from weishi.libs.service import UserManager


class AuthHandler(BaseHandler):
    user_manager = None

    def prepare(self):
        self.user_manager = UserManager(self.db)


class LoginHandler(AuthHandler):
    """
    user login handler
    GET:
        1. login, redirect to main page
        2. not login, render to login template html
    POST:
        check user and password, if match, login
        else, show error
    """

    def get(self):
        if self.current_user:
            self.redirect('/')
            return
        self.render('login.html')

    def post(self, *args, **kwargs):
        u = self.get_argument('user', None)
        p = self.get_argument('password', None)
        result = {'r': 0}
        if not u or not p:
            result['error'] = u'填写的数据不正确'
            self.write(result)
            return
        if EMAIL_REGEX.match(u):
            # 邮箱登录
            user = self.user_manager.get_user_by_email(u)
        else:
            # 用户名登录
            user = self.user_manager.get_user_by_username(u)
        if not user:
            result['error'] = u'账号不存在或密码错误'
            self.write(result)
            return
        if not self.user_manager.login(user, p, self.request.remote_ip):
            result['error'] = u'账号不存在或密码错误'
            self.write(result)
            return
        self.set_secure_cookie('user', user.username, expires_days=15)
        result['r'] = 1
        self.write(result)


class SignUpHandler(AuthHandler):
    """
    sign up handler
    """

    def get(self):
        if self.current_user:
            self.redirect('/')
        else:
            self.render('signup.html')

    def post(self, *args, **kwargs):
        f = SignupForm(self.request.arguments)
        r = {'r': 0}
        if not f.validate():
            errors = f.errors
            r['errors'] = errors
            self.write(r)
            return
        username = f.data['username']
        email = f.data['email']
        password = f.data['password']
        mobile = f.data['mobile']
        user = self.user_manager.get_user_by_username(username)
        if user:
            r['errors'] = {'username': [u'用户名被占用']}
            self.write(r)
            return
        user = self.user_manager.get_user_by_email(email)
        if user:
            r['errors'] = {'email': [u'邮箱被占用']}
            self.write(r)
            return
        self.user_manager.create_user(username, email, password, mobile, self.request.remote_ip)
        self.set_secure_cookie('user', username, expires_days=15)
        r['r'] = 1
        self.write(r)


class LogoutHandler(AuthHandler):
    """
    user log out
    """

    def get(self):
        self.clear_cookie('user')
        self.clear_cookie('aid')
        self.redirect('/')


class UserCheckHandler(AuthHandler):
    """
    check username or email available or not through ajax
    POST:
        1. param: email or username
        2. if available return json {"r", 1}, else {"r", 0}
    """

    def post(self, *args, **kwargs):
        username = self.get_argument('username', None)
        email = self.get_argument('email', None)
        r = {'a': 1}
        if username:
            user = self.user_manager.get_user_by_username(username)
        elif email:
            user = self.user_manager.get_user_by_email(email)
        if user:
            r['a'] = 0
        else:
            r['a'] = 1
        self.write(r)


handlers = [
    (r'/login', LoginHandler),
    (r'/logout', LogoutHandler),
    (r'/user/check', UserCheckHandler),
]