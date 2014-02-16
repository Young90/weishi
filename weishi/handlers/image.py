#coding:utf-8
__author__ = 'young'

from tornado.web import HTTPError
from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
import weishi.libs.image as image_util


class ImageUploadHandler(BaseHandler):
    """jquery-upload上传图片的接口"""

    aid = None

    def prepare(self):
        aid = self.get_cookie('aid', None)
        if not aid:
            raise HTTPError(403, 'aid not correct')
        self.aid = aid

    @authenticated
    def post(self, *args, **kwargs):
        result = {'files': []}
        try:
            file_body = self.request.files['file'][0]['body']
            url = image_util.upload(file_body, self.aid)
            aid = self.get_cookie('aid', None)
            if not aid:
                raise HTTPError(403, 'aid not correct')
            if not url:
                result['error'] = u'上传出错'
                self.write(result)
                return
            _file = {'url': url}
            files = [_file]
            result['files'] = files
            self.write(result)
        except KeyError:
            result['error'] = u'参数不正确或上传图片出错'
            self.write(result)


class UeditorUpload(BaseHandler):
    """ueditor上传图片的接口"""
    aid = None

    def prepare(self):
        aid = self.get_cookie('aid', None)
        if not aid:
            raise HTTPError(403, 'aid not correct')
        self.aid = aid

    @authenticated
    def post(self, *args, **kwargs):
        result = {}
        try:
            file_name = self.request.files['file'][0]['filename']
            file_body = self.request.files['file'][0]['body']
            url = image_util.upload(file_body, self.aid)
            if not url:
                result['error'] = u'上传出错'
                self.write(result)
                return
            result = {'url': url, 'state': 'success', 'title': file_name, 'original': file_name}
            self.write(result)
        except KeyError:
            result['error'] = u'参数不正确或上传图片出错'
            self.write(result)


handlers = [
    (r'/upload', ImageUploadHandler),
    (r'/upload/ueditor', UeditorUpload)
]