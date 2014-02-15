#coding:utf-8
__author__ = 'young'

from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
import weishi.libs.image as image_util


class ImageUploadHandler(BaseHandler):
    """jquery-upload上传图片的接口"""

    @authenticated
    def post(self, *args, **kwargs):
        result = {'files': []}
        try:
            file_body = self.request.files['file'][0]['body']
            url = image_util.upload(file_body, self.current_user.id)
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
            self.finish()
            return


class UeditorUpload(BaseHandler):
    """ueditor上传图片的接口"""

    @authenticated
    def post(self, *args, **kwargs):
        result = {'r': 0}
        try:
            file_body = self.request.files['file'][0]['body']
            url = image_util.upload(file_body, self.current_user.id)
            if not url:
                result['error'] = u'上传出错'
                self.write(result)
                return
            result['r'] = 1
            self.write(result)
            self.finish()
            return
        except KeyError:
            result['error'] = u'参数不正确或上传图片出错'
            self.write(result)
            self.finish()
            return


handlers = [
    (r'/upload', ImageUploadHandler),
    (r'/upload/ueditor', UeditorUpload)
]