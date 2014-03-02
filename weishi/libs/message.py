#coding:utf-8
__author__ = 'Young'

import datetime
import time

from tornado.template import Loader

from weishi import db
from weishi.libs import wei_api


db.connect()
db = db.conn.mysql


def process_message(account, message, path):
    """根据消息类型，处理消息"""
    msg_type = message['MsgType'].lower()
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
    if msg_type == 'event':
        event = message['Event'].lower()
        if event == 'subscribe':
            return _process_subscribe_event(account, message, path)
        if event == 'unsubscribe':
            return _process_unsubscribe_event(account, message)
        if event == 'click':
            return


def _add_single_fan(user, aid):
    """将关注的用户保存到数据库"""
    if db.get('select * from t_fans where openid = %s', user['openid']):
        db.execute('update t_fans set status = 1, date = %s, subscribe_time = %s where openid = %s and aid = %s',
                   datetime.datetime.now(), datetime.datetime.now(), user['openid'], aid)
    else:
        db.execute('insert into t_fans (date, openid, nickname, sex, country, province, city, avatar, '
                   'subscribe_time, language, aid) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                   datetime.datetime.now(), user['openid'], user['nickname'], user['sex'], user['country'],
                   user['province'], user['city'], user['headimgurl'],
                   datetime.datetime.fromtimestamp(int(user['subscribe_time'])), user['language'], aid)


def _process_text_message(aid, message):
    """接受用户发送的文本消息"""
    openid = message['FromUserName']
    content = message['Content']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    db.execute('insert into t_message (type, create_time, message_id, content, status, openid, aid)'
               ' values (%s, %s, %s, %s, %s, %s, %s)', 'text', datetime.datetime.fromtimestamp(int(create_time)),
               msg_id, content, 0, openid, aid)


def _process_image_message(aid, message):
    """接收用户发送的图片消息"""
    openid = message['FromUserName']
    url = message['PicUrl']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    media_id = message['MediaId']
    db.execute('insert into t_message (type, create_time, message_id, url, media_id, status, openid, aid) '
               'values (%s, %s, %s, %s, %s, %s, %s, %s)', 'image', datetime.datetime.fromtimestamp(int(create_time)),
               msg_id, url, media_id, 0, openid, aid)


def _process_voice_message(aid, message):
    """接收用户发送的语音消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    media_id = message['MediaId']
    msg_format = message['Format']
    db.execute('insert into t_message (type, create_time, message_id, media_id, format, status, openid, aid) '
               'values (%s, %s, %s, %s, %s, %s, %s, %s)', 'voice', datetime.datetime.fromtimestamp(int(create_time)),
               msg_id, media_id, msg_format, 0, openid, aid)


def _process_video_message(aid, message):
    """接收用户发送的视频消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    media_id = message['MediaId']
    db.execute('insert into t_message (type, create_time, message_id, media_id, status, openid, aid) '
               'values (%s, %s, %s, %s, %s, %s, %s)', 'video', datetime.datetime.fromtimestamp(int(create_time)),
               msg_id, media_id, 0, openid, aid)


def _process_location_message(aid, message):
    """接收用户发送的位置消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    x = message['Location_X']
    y = message['Location_Y']
    scale = message['Scale']
    label = message['Label']
    db.execute('insert into t_message (type, create_time, message_id, x, y, scale, label, status, openid, aid) '
               'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 'location',
               datetime.datetime.fromtimestamp(int(create_time)),
               msg_id, x, y, scale, label, 0, openid, aid)


def _process_link_message(aid, message):
    """接收用户发送的链接消息"""
    openid = message['FromUserName']
    create_time = message['CreateTime']
    msg_id = message['MsgId']
    url = message['Url']
    db.execute('insert into t_message (type, create_time, message_id, url, status, openid, aid) '
               'values (%s, %s, %s, %s, %s, %s, %s)', 'video', datetime.datetime.fromtimestamp(int(create_time)),
               msg_id, url, 0, openid, aid)


def _process_subscribe_event(account, message, path):
    """
    处理用户关注账号的事件
        1. 将用户信息保存到数据库
        2. 如果有自动回复消息，则回复
    """
    openid = message['FromUserName']
    wei_api.get_user_info(account, openid, _add_single_fan)
    result = {'ToUserName': message['FromUserName'], 'FromUserName': account.wei_account,
              'CreateTime': int(time.time()), 'MsgType': 'text', 'Content': '欢迎关注~'}
    return Loader(path).load('message/text_message.xml').generate(result=result)


def _process_unsubscribe_event(account, message):
    """
    处理用户取消关注账号的事件
    """
    openid = message['FromUserName']
    print 'openid : %s' % openid
    print 'account : %s' % account.aid
    db.execute('update t_fans set status = 0 where openid = %s and aid = %s', openid, account.aid)


def _process_menu_click_event(account, message, path):
    """
    处理用户点击自定义菜单的事件
    """
    openid = message['FromUserName']
    key = message['EventKey']
    auto = db.get('select * from t_auto where mkey = %s and aid = %s', key, account.aid)
    if not auto:
        return None
    if auto.type == 'text':
        result = {'ToUserName': message['FromUserName'], 'FromUserName': account.wei_account,
                  'CreateTime': int(time.time()), 'MsgType': 'text', 'Content': auto.re_content}
        return Loader(path).load('message/text_message.xml').generate(result=result)
    if auto.type == 'single':
        image_article = db.get('select * from t_image_article where id = %s', auto.re_img_art_id)
        if not image_article:
            return None
        