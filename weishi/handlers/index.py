#coding:utf-8
__author__ = 'young'

import time
from tornado.web import RequestHandler
from tornado import template


class IndexHandler(RequestHandler):
    def get(self):
        self.render('account/article.html')

handlers = [
    (r'/index/test', IndexHandler)
]