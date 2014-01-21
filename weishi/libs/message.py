#coding:utf-8
__author__ = 'Young'

import datetime

from weishi import db
from weishi.libs import wei_api


db.connect()
db = db.conn.mysql


def process_message(account, message):
    msg_type = message['MsgType'].lower()
    print msg_type
    if msg_type == 'text':
        return _process_text_message(account.aid, message)
    if msg_type == 'image':
        return _process_image_message(account.aid, message)
    if msg_type == 'voice':
        return _process_voice_message(account.aid, message)
    if msg_type == 'video':
        return _process_video_message(account.aid, message)
    if msg_type == 'location':
        return _process_location_message(account.aid, message)
    if msg_type == 'link':
        return _process_link_message(account.aid, message)


def _add_single_fan(user, aid):
    """将关注的用户保存到数据库"""
    db.execute('insert into t_fans (date, openid, nickname, sex, country, province, city, avatar, '
                    'subscribe_time, language, aid) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    user['openid'], user['nickname'], user['sex'], user['country'], user['province'],
                    user['city'], user['headimgurl'], datetime.datetime.fromtimestamp(int(user['subscribe_time'])),
                    user['language'], aid)

def _process_text_message(aid, message):

    """接受用户发送的文本消息"""
    openid = message['FromUserName']
    content = message['Content']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    db.insert('insert into t_message (type, create_time, message_id, content, status, openid, aid)'
              ' values (%s, %s, %s, %s, %s, %s, %s)', 'text', create_time, msg_id, content, 0, openid, aid)


def _process_image_message(aid, message):
    """接收用户发送的图片消息"""
    openid = message['FromUserName']
    url = message['PicUrl']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    media_id = message['MediaId']
    db.insert('insert into t_message (type, create_time, message_id, url, media_id, status, openid, aid) '
              'values (%s, %s, %s, %s, %s, %s, %s, %s)' % ('image', create_time, msg_id, url, media_id, 0, openid, aid))


def _process_voice_message(aid, message):
    """接收用户发送的语音消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    media_id = message['MediaId']
    msg_format = message['Format']
    db.insert('insert into t_message (type, create_time, message_id, media_id, format, status, openid, aid) '
              'values (%s, %s, %s, %s, %s, %s, %s, %s)', 'voice', create_time, msg_id, media_id, msg_format, 0, openid,
              aid)


def _process_video_message(aid, message):
    """接收用户发送的视频消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    media_id = message['MediaId']
    db.insert('insert into t_message (type, create_time, message_id, media_id, status, openid, aid) '
              'values (%s, %s, %s, %s, %s, %s, %s)', 'video', create_time, msg_id, media_id, 0, openid, aid)


def _process_location_message(aid, message):
    """接收用户发送的位置消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    x = message['Location_X']
    y = message['Location_Y']
    scale = message['Scale']
    label = message['Label']
    db.insert('insert into t_message (type, create_time, message_id, x, y, scale, label, status, openid, aid) '
              'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 'video', create_time, msg_id, x, y, scale, label, 0,
              openid, aid)


def _process_link_message(aid, message):
    """接收用户发送的链接消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    url = message['Url']
    db.insert('insert into t_message (type, create_time, message_id, url, status, openid, aid) '
              'values (%s, %s, %s, %s, %s, %s, %s)', 'video', create_time, msg_id, url, 0, openid, aid)


def _process_subscribe_event(account, message):
    """
    处理用户关注账号的事件
        1. 将用户信息保存到数据库
        2. 如果有自动回复消息，则回复
    """
    openid = message['FromUserName']
    wei_api.get_user_info(account, openid, _add_single_fan)