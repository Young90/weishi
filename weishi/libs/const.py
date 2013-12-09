#coding:utf-8
#定义一些系统常量
__author__ = 'young'
import re

DOMAIN_NAME = 'http://wsmt.sinaapp.com'
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
    BUCKET_NAME = "weishi"
    URL_PREFIX = "http://weishi.u.qiniudn.com/%s"
    URL_PREFIX_NO_HTTP = "weishi.u.qiniudn.com/%s"
    FOLDER_ARTICLE = "article"
    FOLDER_AVATAR = "avatar"
    MIME_TYPE_JPG = "image/jpeg"