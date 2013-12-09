#coding:utf-8
from weishi.handlers import admin, front, user, api, account

__author__ = 'young'

handlers = []

handlers.extend(front.handlers)
handlers.extend(admin.handlers)
handlers.extend(user.handlers)
handlers.extend(api.handlers)
handlers.extend(account.handlers)