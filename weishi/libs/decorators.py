#coding:utf-8
__author__ = 'young'

import functools


def authenticated(method):
    """
    only allow login user to operate
    """

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            self.redirect("/login")
            return
        return method(self, *args, **kwargs)

    return wrapper