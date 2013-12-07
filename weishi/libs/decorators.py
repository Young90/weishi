#coding:utf-8
__author__ = 'young'

import functools


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