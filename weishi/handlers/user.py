#coding:utf-8
__author__ = 'young'

import hashlib
from weishi.libs.handler import BaseHandler
from weishi.libs.const import EMAIL_REGEX, Role
from weishi.form.user_form import SignupForm


class AuthHandler(BaseHandler):
    # user login, update info
    def _login(self, user):
        self.db.execute("update t_user set login_ip = %s, login_date = NOW(), login_count = %s "
                        "where id = %s", self.request.remote_ip, user.login_count + 1, user.id)
        self.set_secure_cookie("user", user.username, expires_days=15)

    # create user
    def _create_user(self, username, email, password, mobile):
        self.db.execute("insert into t_user (date, username, email, password, mobile, signup_ip, login_ip, login_date)"
                        " values (NOW(), %s, %s, %s, %s, %s, %s, NOW())", username, email, password, mobile,
                        self.request.remote_ip, self.request.remote_ip)
        self.set_secure_cookie("user", username, expires_days=15)


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
            self.redirect("/")
            return
        self.render("login.html")

    def post(self, *args, **kwargs):
        u = self.get_argument("user", None)
        p = self.get_argument("password", None)
        self.db
        if not u or not p:
            self.render("login.html", error="填写的数据不正确")
            return
        if EMAIL_REGEX.match(u):
            # 邮箱登录
            user = self.db.get("select * from t_user where email = %s", u)
        else:
            # 用户名登录
            user = self.db.get("select * from t_user where username = %s", u)
        if not user:
            self.render("login.html", error="账号不存在或密码错误")
            return
        m = hashlib.md5()
        m.update(p + Role.SALT)
        if m.hexdigest() != user.password:
            self.render("login.html", error="账号不存在或密码错误")
            return
        self._login(user)
        self.redirect("/")


class SignUpHandler(AuthHandler):
    """
    sign up handler
    """

    def get(self):
        if self.current_user:
            self.redirect("/")
        else:
            self.render("signup.html")

    def post(self, *args, **kwargs):
        signup_form = SignupForm(self.request.arguments)
        length = real_len(signup_form.data['username'])
        if length < 4 or length > 20:
            self.render("signup.html", form=signup_form, error='用户名长度在4-20之间，中文为两个字符！')
            return
        if not signup_form.validate():
            errors = signup_form.errors
            error = ''.join(errors.values()[0][0])
            self.render("signup.html", form=signup_form, error=error)
            return
        username = signup_form.data['username']
        email = signup_form.data['email']
        password = signup_form.data['password']
        mobile = signup_form.data['mobile']
        user = self.db.get("select * from t_user where username = %s", username)
        if user:
            print u"用户名被注册！"
            self.render("signup.html", form=signup_form, error="用户名被占用！")
            return
        user = self.db.get("select * from t_user where email = %s", email)
        if user:
            print u"邮箱被占用！"
            self.render("signup.html", form=signup_form, error="邮箱被占用！")
            return
        m = hashlib.md5()
        m.update(password + Role.SALT)
        password = m.hexdigest()
        self._create_user(username, email, password, mobile)
        self.redirect("/")


def real_len(username):
    length = len(username)
    utf_len = len(username.encode('utf-8'))
    length += (utf_len - length) / 2
    return length


class LogoutHandler(AuthHandler):
    """
    user log out
    """

    def get(self):
        self.clear_cookie("user")
        self.redirect("/")


class UserCheckHandler(AuthHandler):
    """
    check username or email available or not through ajax
    POST:
        1. param: email or username
        2. if available return json {"r", 1}, else {"r", 0}
    """

    def post(self, *args, **kwargs):
        username = self.get_argument("username", None)
        email = self.get_argument("email", None)
        r = {"a": 1}
        if username:
            user = self.db.get("select * from t_user where username = %s", username)
        elif email:
            user = self.db.get("select * from t_user where email = %s", email)
        if user:
            r['a'] = 0
        else:
            r['a'] = 1
        self.write(r)


handlers = [
    (r'/login', LoginHandler),
    (r'/signup', SignUpHandler),
    (r'/logout', LogoutHandler),
    (r'/user/check', UserCheckHandler),
]