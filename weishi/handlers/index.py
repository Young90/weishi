#coding:utf-8
__author__ = 'young'

import time
from tornado.web import RequestHandler
from tornado import template


class IndexHandler(RequestHandler):
    def get(self):
        result = {'ToUserName': 'toUser', 'FromUserName': 'developer', 'CreateTime': int(time.time()),
                  'Articles': [{}, {}], 'MsgType': 'text', 'Content': u'欢迎关注'}
        self.write(template.Loader(self.get_template_path())
        .load(name='text_message.xml', parent_path='message').generate(result=result))


handlers = [
    (r'/index/test', IndexHandler)
]