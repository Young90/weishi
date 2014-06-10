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
        return method(self, *args, **kwargs)

    return wrapper


def form_auth(method):
    """自定义表单权限"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.account.form:
            raise HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper


def menu_auth(method):
    """自定义菜单权限"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.account.menu:
            raise HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper


def card_auth(method):
    """会员卡权限"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.account.card:
            raise HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper


def site_auth(method):
    """微官网权限"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.account.site:
            raise HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper


def impact_auth(method):
    """用户印象权限"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.account.impact:
            raise HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper


def event_auth(method):
    """微活动权限"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.account.event:
            raise HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper


def canyin_auth(method):
    """餐饮权限"""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.account.canyin:
            raise HTTPError(404)
        return method(self, *args, **kwargs)

    return wrapper