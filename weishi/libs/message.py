#coding:utf-8
__author__ = 'Young'

from weishi import db

db.connect()
db = db.conn.mysql


def process_message(account, message):
    msg_type = message['MsgType'].lower()
    print msg_type
    if msg_type == 'text':
        return _process_text_message(account, message)


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
