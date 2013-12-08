#coding:utf-8
__author__ = 'young'

import os
from tornado import web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop


class Application(web.Application):
    def __init__(self):
        from weishi.urls import handlers

        settings = dict(
            debug=True,
            template_path=os.path.join(os.path.dirname(__file__), "weishi/templates"),
            static_path=os.path.join(os.path.dirname(__file__), "weishi/static"),
            xsrf_cookies=True,
            cookie_secret="my secret",
        )

        handlers.extend([
            (r'/(.*)', web.StaticFileHandler, {'path': settings['static_path']}),
        ])
        super(Application, self).__init__(handlers, **settings)


def main():
    http_server = HTTPServer(Application())
    port = 8888
    http_server.bind(port)
    http_server.start()
    IOLoop.instance().start()


if __name__ == "__main__":
    main()