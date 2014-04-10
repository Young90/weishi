#coding:utf-8
__author__ = 'young'

import functools
from tornado.web import HTTPError


def authenticated(method):
    """
    定义一些操作位授权操作
    如果没有登录，则跳转到登录页面
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.redirect("/login")
            return
        return method(self, *args, **kwargs)

    return wrapper


def admin(method):
    """只能由管理员进行的操作"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.current_user.role != 1:
            raise HTTPError(404)
            return
        return method(self, *args, **kwargs)
    return wrapper