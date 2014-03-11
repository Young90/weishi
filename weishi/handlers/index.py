#coding:utf-8
__author__ = 'young'

import json
import urllib
from tornado.web import RequestHandler
from tornado.web import HTTPError

from weishi.libs.service import FormManager
from weishi.libs.handler import BaseHandler


class IndexHandler(RequestHandler):
    def get(self):
        self.render('account/article.html')


class FormHandler(BaseHandler):
    """浏览表单"""

    form_manager = None

    def prepare(self):
        self.form_manager = FormManager(self.db)

    def get(self, fid):
        """返回表单页面"""
        form = self.form_manager.get_form_by_fid(fid)
        if not form:
            raise HTTPError(404)
        items = json.loads(form.content)
        self.render('front/form.html', form=form, items=items)

    def post(self, *args, **kwargs):
        """提交表单"""
        form = self.form_manager.get_form_by_fid(args[0])
        items = self.request.body.split('&')
        result = {}
        for item in items:
            k, v = map(urllib.unquote, item.split('='))
            result[k] = v
        self.form_manager.save_input_to_form_content(form.fid, json.dumps(result, ensure_ascii=False))
        self.render('front/form-success.html')


handlers = [
    (r'/index/test', IndexHandler),
    (r'/form/([^/]+)', FormHandler),
]