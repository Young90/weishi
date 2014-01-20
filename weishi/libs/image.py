#coding:utf-8
import random
import string

import qiniu.conf
import qiniu.io
import qiniu.rs
import qiniu.rsf
from const import Image

import weishi.conf

qiniu.conf.ACCESS_KEY = weishi.conf.qiniu_access_key
qiniu.conf.SECRET_KEY = weishi.conf.qiniu_secret_key
bucket_name = Image.BUCKET_NAME
policy = qiniu.rs.PutPolicy(bucket_name)
extra = qiniu.io.PutExtra()
extra.mime_type = Image.MIME_TYPE_JPG

url_prefix = Image.URL_PREFIX
url_prefix_no_http = Image.URL_PREFIX_NO_HTTP


def r(length):
    lib = string.ascii_letters
    return ''.join([random.choice(lib) for i in range(0, length)])


def upload(file_content, prefix):
    """
    上传图片到七牛云存储
    返回图片完整地址
    """
    key = prefix + "_" + r(16)
    ret, err = qiniu.io.put(policy.token(), key, file_content, extra)
    if err is None:
        return Image.URL_PREFIX % ret['key']
    else:
        return None


def list_all(prefix=None):
    """
    列出所有图片
    """
    marker = None
    err = None
    results = []
    while err is None:
        ret, err = qiniu.rsf.Client().list_prefix('weishi', prefix=prefix, marker=marker)
        marker = ret.get('marker', None)
        for item in ret['items']:
            results.append(Image.URL_PREFIX % item['key'])
    return results