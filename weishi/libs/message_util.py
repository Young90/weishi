#coding:utf-8
__author__ = 'young'

import time
from tornado.template import Loader


def image_article_group_to_message(article_list, from_message, path, wei_account):
    """将图文消息转换为微信需要的数据格式"""
    items = []
    print article_list
    for article in article_list:
        item = {'title': article.title, 'summary': article.summary, 'thumb': article.image, 'url': article.link}
        items.append(item)
    result = {'ToUserName': from_message['FromUserName'], 'FromUserName': wei_account,
              'CreateTime': int(time.time()), 'count': len(items), 'items': items}
    return Loader(path).load('message/image_message.xml').generate(result=result)


def text_response_to_message(content, from_message, path, wei_account):
    """将文本回复转换为微信所需的数据格式"""
    result = {'ToUserName': from_message['FromUserName'], 'FromUserName': wei_account,
              'CreateTime': int(time.time()), 'MsgType': 'text', 'Content': content}
    return Loader(path).load('message/text_message.xml').generate(result=result)