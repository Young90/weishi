# coding:utf-8
__author__ = 'Young'

from weishi.libs import wei_api
from weishi.libs.service import ImageArticleManager, FansManager, AutoManager, MessageManager, CardManager, \
    AutoKeywordManager
from weishi.libs import message_util, key_util


class Message():
    image_article_manager = None
    fans_manager = None
    auto_manager = None
    message_manager = None
    card_manager = None
    auto_keyword_manager = None

    def __init__(self, db):
        self.image_article_manager = ImageArticleManager(db)
        self.fans_manager = FansManager(db)
        self.auto_manager = AutoManager(db)
        self.message_manager = MessageManager(db)
        self.card_manager = CardManager(db)
        self.auto_keyword_manager = AutoKeywordManager(db)

    def process_message(self, account, message, path):
        """根据消息类型，处理消息"""
        openid = message['FromUserName']
        fans = self.fans_manager.get_fans_by_openid_aid(openid, account.aid)
        if not fans:
            wei_api.get_user_info(account, openid, self._add_single_fan)
        msg_type = message['MsgType'].lower()
        if msg_type == 'text':
            return self._process_text_message(account, message, path)
        if msg_type == 'image':
            return self._process_image_message(account, message, path)
        if msg_type == 'voice':
            return self._process_voice_message(account.aid, message)
        if msg_type == 'video':
            return self._process_video_message(account.aid, message)
        if msg_type == 'location':
            return self._process_location_message(account.aid, message)
        if msg_type == 'link':
            return self._process_link_message(account.aid, message)
        if msg_type == 'event':
            event = message['Event'].lower()
            if event == 'subscribe':
                return self._process_subscribe_event(account, message, path)
            if event == 'unsubscribe':
                return self._process_unsubscribe_event(account, message)
            if event == 'click':
                return self._process_menu_click_event(account, message, path)

    def _add_single_fan(self, user, aid, openid):
        """将关注的用户保存到数据库"""
        if self.fans_manager.get_fans_by_id(openid):
            # 如果用户已经取消关注后再关注
            self.fans_manager.re_subscribe_fans(openid, aid)
        else:
            if not user:
                self.fans_manager.save_single_fans_without_info(aid, openid)
            else:
                self.fans_manager.save_single_fans(user, aid)

    def _process_text_message(self, account, message, path):
        """接受用户发送的文本消息
           1. 保存到数据库
           2. 匹配有没有定义的回复，有则回复
        """
        self.message_manager.receive_text_message(message, account.aid)
        content = message['Content']
        auto = self.auto_keyword_manager.get_auto_by_word(account.aid, content)
        if not auto:
            _list = self.auto_keyword_manager.list_auto_by_wild(account.aid)
            for _l in _list:
                if _l.word in content:
                    auto = _l
        if auto:
            if auto.re_type == 'text':
                return message_util.text_response_to_message(auto.re_content, message, path, account.wei_account)
            elif auto.re_type == 'single':
                image_article = self.image_article_manager.get_image_article_by_id(auto.re_img_art_id)
                return message_util.image_article_group_to_message([image_article], message, path, account.wei_account)
            elif auto.re_type == 'multi':
                image_article_group = self.image_article_manager.get_multi_image_article_by_id(auto.re_img_art_id)
                if not image_article_group:
                    return None
                id_list = [image_article_group.id1, image_article_group.id2, image_article_group.id3,
                           image_article_group.id4,
                           image_article_group.id5]
                id_list = filter(lambda a: a != 0, id_list)
                article_list = []
                for _id in id_list:
                    article_list.append(self.image_article_manager.get_image_article_by_id(_id))
                print article_list
                return message_util.image_article_group_to_message(article_list, message, path, account.wei_account)

    def _process_image_message(self, account, message, path):
        """接收用户发送的图片消息"""
        aid = account.aid
        openid = message['FromUserName']
        self.message_manager.receive_image_message(message, aid)
        auto = self.auto_manager.get_image_auto(aid)
        if auto:
            # 回复验证码
            code = key_util.generate_digits(8)
            if self.auto_manager.has_code(aid, openid):
                content = auto.re_content.split('&&')[2]
            elif self.auto_manager.count_code_response(aid) >= auto.num:
                content = auto.re_content.split('&&')[1]
            else:
                content = auto.re_content.split('&&')[0].replace('#code#', code)
                self.auto_manager.save_code_response(openid, aid, code)
            return message_util.text_response_to_message(content, message, path, account.wei_account)

    def _process_voice_message(self, aid, message):
        """接收用户发送的语音消息"""
        self.message_manager.receive_voice_message(message, aid)

    def _process_video_message(self, aid, message):
        """接收用户发送的视频消息"""
        self.message_manager.receive_video_message(message, aid)

    def _process_location_message(self, aid, message):
        """接收用户发送的位置消息"""
        self.message_manager.receive_location_message(message, aid)

    def _process_link_message(self, aid, message):
        """接收用户发送的链接消息"""
        self.message_manager.receive_link_message(message, aid)

    def _process_subscribe_event(self, account, message, path):
        """
        处理用户关注账号的事件
            1. 将用户信息保存到数据库
            2. 如果有自动回复消息，则回复
        """
        openid = message['FromUserName']
        wei_api.get_user_info(account, openid, self._add_single_fan)
        auto = self.auto_manager.get_follow_auto(account.aid)
        if not auto:
            return
        if auto.type == 'text':
            return message_util.text_response_to_message(auto.re_content, message, path, account.wei_account)
        if auto.type == 'single':
            image_article = self.image_article_manager.get_image_article_by_id(auto.re_img_art_id)
            return message_util.image_article_group_to_message([image_article], message, path, account.wei_account)
        if auto.type == 'multi':
            image_article_group = self.image_article_manager.get_multi_image_article_by_id(auto.re_img_art_id)
            if not image_article_group:
                return None
            id_list = [image_article_group.id1, image_article_group.id2, image_article_group.id3,
                       image_article_group.id4,
                       image_article_group.id5]
            id_list = filter(lambda a: a != 0, id_list)
            article_list = []
            for _id in id_list:
                article_list.append(self.image_article_manager.get_image_article_by_id(_id))
            return message_util.image_article_group_to_message(article_list, message, path, account.wei_account)

    def _process_unsubscribe_event(self, account, message):
        """
        处理用户取消关注账号的事件
        """
        openid = message['FromUserName']
        self.fans_manager.unsubscribe_fans(openid, account.aid)

    def _process_menu_click_event(self, account, message, path):
        """
        处理用户点击自定义菜单的事件
        """
        key = message['EventKey']
        print '_process_menu_click_event : key ------ %s' % key
        auto = self.auto_manager.get_auto_by_key(key)
        if not auto:
            return None
        if auto.type == 'text':
            return message_util.text_response_to_message(auto.re_content, message, path, account.wei_account)
        if auto.type == 'single':
            image_article = self.image_article_manager.get_image_article_by_id(auto.re_img_art_id)
            return message_util.image_article_group_to_message([image_article], message, path, account.wei_account)
        if auto.type == 'card':
            card = self.card_manager.get_card_by_aid(account.aid)
            member = self.card_manager.get_user_card_info(card.cid, message['FromUserName'])
            return message_util.card_response_to_message(card, member, message, path, account.wei_account)
        if auto.type == 'multi':
            image_article_group = self.image_article_manager.get_multi_image_article_by_id(auto.re_img_art_id)
            if not image_article_group:
                return None
            id_list = [image_article_group.id1, image_article_group.id2, image_article_group.id3,
                       image_article_group.id4,
                       image_article_group.id5]
            id_list = filter(lambda a: a != 0, id_list)
            print id_list
            article_list = self.image_article_manager.get_image_article_by_id_list(id_list)
            print 'article list ---------- %s ' % article_list
            return message_util.image_article_group_to_message(article_list, message, path, account.wei_account)