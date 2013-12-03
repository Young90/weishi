#coding:utf-8
from weishi import db
from weishi.libs import const

__author__ = 'young'

from tornado.web import RequestHandler, HTTPError


class BaseHandler(RequestHandler):
    _first_running = True
    db = None

    def __init__(self, application, request, **kwargs):
        if BaseHandler._first_running:
            self._after_prefork()
            BaseHandler._first_running = False

        super(BaseHandler, self).__init__(application, request, **kwargs)

    def _after_prefork(self):
        db.connect()
        BaseHandler.db = db.conn.mysql

    def get_current_user(self):
        username = self.get_secure_cookie("user")
        if not username:
            return None
        return self.db.get("select * from t_user where username = %s", username)

    @property
    def is_admin(self):
        return self.current_user.role >= const.Role.ADMIN


class ErrorHandler(BaseHandler):
    """Default 404: Not Found handler."""

    def prepare(self):
        super(ErrorHandler, self).prepare()
        raise HTTPError(404)