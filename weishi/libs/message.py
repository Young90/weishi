#coding:utf-8
__author__ = 'Young'

from weishi import db
from weishi.libs import wei_api
from weishi.libs.service import ImageArticleManager, FansManager, AutoManager, MessageManager, CardManager, \
    AutoKeywordManager
from weishi.libs import message_util

db.connect()
db = db.conn.mysql

image_article_manager = ImageArticleManager(db)
fans_manager = FansManager(db)
auto_manager = AutoManager(db)
message_manager = MessageManager(db)
card_manager = CardManager(db)
auto_keyword_manager = AutoKeywordManager(db)


def process_message(account, message, path):
    """根据消息类型，处理消息"""
    msg_type = message['MsgType'].lower()
    if msg_type == 'text':
        return _process_text_message(account, message, path)
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
            return _process_menu_click_event(account, message, path)


def _add_single_fan(user, aid):
    """将关注的用户保存到数据库"""
    openid = user['openid']
    if fans_manager.get_fans_by_id(openid):
        # 如果用户已经取消关注后再关注
        fans_manager.re_subscribe_fans(openid, aid)
    else:
        # 第一次关注，保存到数据库
        fans_manager.save_single_fans(user, aid)


def _process_text_message(account, message, path):
    """接受用户发送的文本消息
       1. 保存到数据库
       2. 匹配有没有定义的回复，有则回复
    """
    message_manager.receive_text_message(message, account.aid)
    auto = auto_keyword_manager.get_auto_by_word(account.aid, message['Content'])
    if auto:
        if auto.re_type == 'text':
            return message_util.text_response_to_message(auto.re_content, message, path, account.wei_account)
        elif auto.re_type == 'single':
            image_article = image_article_manager.get_image_article_by_id(auto.re_img_art_id)
            return message_util.image_article_group_to_message([image_article], message, path, account.wei_account)
        elif auto.re_type == 'multi':
            image_article_group = image_article_manager.get_multi_image_article_by_id(auto.re_img_art_id)
            if not image_article_group:
                return None
            id_list = [image_article_group.id1, image_article_group.id2, image_article_group.id3, image_article_group.id4,
                       image_article_group.id5]
            id_list = filter(lambda a: a != 0, id_list)
            article_list = []
            for _id in id_list:
                article_list.append(image_article_manager.get_image_article_by_id(_id))
            print article_list
            return message_util.image_article_group_to_message(article_list, message, path, account.wei_account)


def _process_image_message(aid, message):
    """接收用户发送的图片消息"""
    message_manager.receive_image_message(message, aid)


def _process_voice_message(aid, message):
    """接收用户发送的语音消息"""
    message_manager.receive_voice_message(message, aid)


def _process_video_message(aid, message):
    """接收用户发送的视频消息"""
    message_manager.receive_video_message(message, aid)


def _process_location_message(aid, message):
    """接收用户发送的位置消息"""
    message_manager.receive_location_message(message, aid)


def _process_link_message(aid, message):
    """接收用户发送的链接消息"""
    message_manager.receive_link_message(message, aid)


def _process_subscribe_event(account, message, path):
    """
    处理用户关注账号的事件
        1. 将用户信息保存到数据库
        2. 如果有自动回复消息，则回复
    """
    openid = message['FromUserName']
    wei_api.get_user_info(account, openid, _add_single_fan)
    auto = auto_manager.get_follow_auto(account.aid)
    if auto.type == 'text':
        return message_util.text_response_to_message(auto.re_content, message, path, account.wei_account)
    if auto.type == 'single':
        image_article = image_article_manager.get_image_article_by_id(auto.re_img_art_id)
        return message_util.image_article_group_to_message([image_article], message, path, account.wei_account)
    if auto.type == 'multi':
        image_article_group = image_article_manager.get_multi_image_article_by_id(auto.re_img_art_id)
        if not image_article_group:
            return None
        id_list = [image_article_group.id1, image_article_group.id2, image_article_group.id3, image_article_group.id4,
                   image_article_group.id5]
        id_list = filter(lambda a: a != 0, id_list)
        article_list = []
        for _id in id_list:
            article_list.append(image_article_manager.get_image_article_by_id(_id))
        return message_util.image_article_group_to_message(article_list, message, path, account.wei_account)


def _process_unsubscribe_event(account, message):
    """
    处理用户取消关注账号的事件
    """
    openid = message['FromUserName']
    fans_manager.unsubscribe_fans(openid, account.aid)


def _process_menu_click_event(account, message, path):
    """
    处理用户点击自定义菜单的事件
    """
    key = message['EventKey']
    print '_process_menu_click_event : key ------ %s' % key
    auto = auto_manager.get_auto_by_key(key)
    if not auto:
        return None
    if auto.type == 'text':
        return message_util.text_response_to_message(auto.re_content, message, path, account.wei_account)
    if auto.type == 'single':
        image_article = image_article_manager.get_image_article_by_id(auto.re_img_art_id)
        return message_util.image_article_group_to_message([image_article], message, path, account.wei_account)
    if auto.type == 'card':
        card = card_manager.get_card_by_aid(account.aid)
        member = card_manager.get_user_card_info(card.cid, message['FromUserName'])
        return message_util.card_response_to_message(card, member, message, path, account.wei_account)
    if auto.type == 'multi':
        image_article_group = image_article_manager.get_multi_image_article_by_id(auto.re_img_art_id)
        if not image_article_group:
            return None
        id_list = [image_article_group.id1, image_article_group.id2, image_article_group.id3, image_article_group.id4,
                   image_article_group.id5]
        id_list = filter(lambda a: a != 0, id_list)
        article_list = image_article_manager.get_image_article_by_id_list(','.join(str(x) for x in id_list))
        return message_util.image_article_group_to_message(article_list, message, path, account.wei_account)