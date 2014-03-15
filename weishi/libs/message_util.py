#coding:utf-8
__author__ = 'young'

import time
from tornado.template import Loader


def image_article_group_to_message(article_list, from_message, path, wei_account):
    """将图文消息转换为微信需要的数据格式"""
    items = []
    for article in article_list:
        item = {'title': article.title, 'summary': article.summary, 'thumb': article.image, 'url': article.link}
        items.append(item)
    result = {'ToUserName': from_message['FromUserName'], 'FromUserName': wei_account,
              'CreateTime': int(time.time()), 'count': len(items), 'items': items}
    return Loader(path).load('message/image_message.xml').generate(result=result)


def card_response_to_message(card, member, from_message, path, wei_account):
    """将会员卡回复转换为图文消息"""
    if member:
        summary = '您的会员卡号是%s' % str(member.num)
    else:
        summary = '成为会员，享受更多特权'
    openid = from_message['FromUserName']
    link = 'http://wsmt.sinaapp.com/card/' + card.cid + '?i=' + openid
    result = {'ToUserName': openid, 'FromUserName': wei_account, 'CreateTime': int(time.time()), 'count': 1,
              'items': [{'title': '您的会员卡', 'summary': summary, 'thumb': '', 'url': link}]}
    return Loader(path).load('message/image_message.xml').generate(result=result)


def text_response_to_message(content, from_message, path, wei_account):
    """将文本回复转换为微信所需的数据格式"""
    result = {'ToUserName': from_message['FromUserName'], 'FromUserName': wei_account,
              'CreateTime': int(time.time()), 'MsgType': 'text', 'Content': content}
    return Loader(path).load('message/text_message.xml').generate(result=result)