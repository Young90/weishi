#coding:utf-8
__author__ = 'young'

import functools
from tornado.web import HTTPError


def authenticated(method):
    """
    保证是已经登录的用户进行某些操作
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            # TODO 如果用户没有登录，跳转到登录页面
            return HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper


def admin(method):
    """
    保证是管理员用户进行某些操作
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # TODO 如果用户没有登录，跳转到登录页面
        if not self.current_user:
            self.redirect("/admin/login")
            return
        # TODO 如果用户不是管理员，跳转到首页
        elif not self.is_admin:
            return HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper