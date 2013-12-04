#coding:utf-8
import random
import string

from qiniu import conf, io, rs, rsf
from const import Image

import weishi.conf


conf.ACCESS_KEY = weishi.conf.qiniu_access_key
conf.SECRET_KEY = weishi.conf.qiniu_secret_key
bucket_name = Image.BUCKET_NAME
policy = rs.PutPolicy(bucket_name)
extra = io.PutExtra()
extra.mime_type = Image.MIME_TYPE_JPG

url_prefix = Image.URL_PREFIX
url_prefix_no_http = Image.URL_PREFIX_NO_HTTP


def r(length):
    lib = string.ascii_uppercase
    return ''.join([random.choice(lib) for i in range(0, length)])


def upload(file_content, prefix):
    """
    上传图片到七牛云存储
    返回图片完整地址
    """
    key = prefix + "_" + r(16)
    ret, err = io.put(policy.token(), key, file_content, extra)
    if err is None:
        return Image.URL_PREFIX % ret["key"]
    else:
        return None


def image_list(prefix):
    """
    列出所有图片
    """
    rets, err = rsf.Client().list_prefix("zhuangxiutai", prefix=prefix)
    return rets