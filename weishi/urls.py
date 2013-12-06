#coding:utf-8
from weishi.handlers import admin, front, user, api
from weishi.libs.handler import ErrorHandler

__author__ = 'young'

handlers = []

handlers.extend(front.handlers)
handlers.extend(admin.handlers)
handlers.extend(user.handlers)
handlers.extend(api.handlers)
handlers.append((r".*", ErrorHandler))