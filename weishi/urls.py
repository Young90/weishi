#coding:utf-8
from weishi.handlers import admin, front, user, api, account, index, article, material, image, event, task

__author__ = 'young'

handlers = []

handlers.extend(front.handlers)
handlers.extend(admin.handlers)
handlers.extend(user.handlers)
handlers.extend(api.handlers)
handlers.extend(account.handlers)
handlers.extend(index.handlers)
handlers.extend(article.handlers)
handlers.extend(material.handlers)
handlers.extend(image.handlers)
handlers.extend(event.handlers)
handlers.extend(task.handlers)