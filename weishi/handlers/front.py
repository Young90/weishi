#coding:utf-8
__author__ = 'young'

from weishi.libs.handler import BaseHandler


class IndexHandler(BaseHandler):
    def get(self):
        self.render("index.html")


class HelloHandler(BaseHandler):
    def get(self, name):
        print name
        hello = "Hello %s!" % name
        self.write(hello)


handlers = [
    (r"/", IndexHandler),
    (r"/hello/(.*)", HelloHandler),
]
