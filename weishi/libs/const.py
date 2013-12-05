#coding:utf-8
#定义一些系统常量
__author__ = 'young'
import re

# TODO 完善domain name
DOMAIN_NAME = ''
EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")


class Role(object):
    """
    定义用户角色属性
    """
    NORMAL = 0
    ADMIN = 1
    SALT = "this is salt"


class Image(object):
    """
    更图片相关的常量
    """
    BUCKET_NAME = "zhuangxiutai"
    URL_PREFIX = "http://zhuangxiutai.u.qiniudn.com/%s"
    URL_PREFIX_NO_HTTP = "zhuangxiutai.u.qiniudn.com/%s"
    FOLDER_ARTICLE = "article"
    MIME_TYPE_JPG = "image/jpeg"