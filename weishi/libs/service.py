# coding:utf-8
__author__ = 'young'

import hashlib
import time
import datetime
from weishi.libs.const import Role


class Base:
    db = None

    def __init__(self, db):
        self.db = db


class UserManager(Base):
    def create_user(self, username, email, password, mobile, ip):
        """用户创建账号"""
        self.db.execute('insert into t_user (date, username, email, password, mobile, signup_ip, login_ip, login_date)'
                        ' values (NOW(), %s, %s, %s, %s, %s, %s, NOW())', username, email,
                        self._generate_password(password), mobile, ip, ip)

    @staticmethod
    def _generate_password(password):
        """密码加密"""
        m = hashlib.md5()
        m.update(password + Role.SALT)
        p = m.hexdigest()
        return p

    def login(self, user, password, ip):
        """用户登录，如果成功，更新登录信息，返回True
        如果失败，返回False"""
        p = self._generate_password(password)
        print p
        print user.password
        if user.password == p:
            self.db.execute('update t_user set login_ip = %s, login_date = NOW(), login_count = %s '
                            'where id = %s', ip, user.login_count + 1, user.id)
            return True
        return False

    def get_user_by_id(self, _id):
        """根据id获取用户"""
        return self.db.get('select * from t_user where id = %s', int(_id))

    def get_user_by_email(self, email):
        """根据邮箱获取用户"""
        return self.db.get('select * from t_user where email = %s', email)

    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        return self.db.get('select * from t_user where username = %s', username)

    def list_users(self, start, end):
        """列出用户"""
        return self.db.query('select * from t_user order by id limit %s, %s', int(start), int(end))


class AccountManager(Base):
    def list_accounts(self, start, end):
        """列出所有的微信账号"""
        return self.db.query('select * from t_account limit %s, %s', start, end)

    def create_account(self, wei_id, wei_name, wei_account, token, aid, avatar, user_id):
        """添加微信公众账号"""
        self.db.execute("insert into t_account (date, wei_id, wei_name, wei_account, token, aid, avatar, user_id) "
                        "values (NOW(), %s, %s, %s, %s, %s, %s, %s)", wei_id, wei_name, wei_account, token, aid, avatar,
                        user_id)

    def update_account_app_info(self, aid, app_id, app_secret, wei_account):
        """更新账号app信息"""
        self.db.execute('update t_account set app_id = %s, app_secret = %s, wei_account = %s where aid = %s',
                        app_id, app_secret, wei_account, aid)

    def delete_account(self, aid, user_id):
        """删除公众账号"""
        self.db.execute('delete from t_account where aid = %s and user_id = %s', aid, user_id)

    def change_account_user(self, aid, user_id):
        """修改公众号的用户"""
        self.db.execute('update t_account set user_id = %s where aid = %s', int(user_id), aid)

    def get_account_by_id(self, _id):
        """根据id获取公众账号"""
        return self.db.get('select * from t_account where id = %s', _id)

    def get_account_by_aid(self, aid):
        """根据aid获取公众账号"""
        return self.db.get('select * from t_account where aid = %s', aid)

    def update_account_token(self, aid, access_token, expires):
        """当access_token过期后，获取微信的access_token"""
        self.db.execute('update t_account set access_token = %s, expires = %s where aid = %s', access_token, expires,
                        aid)

    def check_account(self, aid):
        """经过微信服务器验证的，将checked设为1"""
        self.db.execute('update t_account set checked = 1 where aid = %s', aid)

    def change_auth(self, _id, menu, card, form, site, impact, event, canyin):
        """修改权限"""
        self.db.execute(
            'update t_account set menu = %s, card = %s, form = %s, site = %s, impact = %s, event = %s, canyin = %s'
            ' where id = %s', menu, card, form, site, impact, event, canyin, _id)


class FansManager(Base):
    def get_fans(self, aid, group_id, start, end):
        if group_id:
            return self.db.query('select * from t_fans where aid = %s and group_id = %s order by id desc limit %s, %s',
                                 aid, group_id, int(start), int(end))
        return self.db.query('select * from t_fans where aid = %s order by id desc limit %s, %s', aid, int(start),
                             int(end))

    def get_fans_group_by_id(self, aid, _id):
        """根据id获取分组"""
        return self.db.get('select * from t_fans_group where aid = %s and id = %s', aid, _id)

    def remove_fans_group(self, aid, _id):
        """删除粉丝分组"""
        self.db.execute('update t_fans set group_id = 0 where group_id = %s', _id)
        self.db.execute('delete from t_fans_group where id = %s', _id)

    def get_fans_group_by_name(self, aid, name):
        """根据name获取分组"""
        return self.db.get('select * from t_fans_group where aid = %s and name = %s', aid, name)

    def new_fans_group(self, aid, name):
        """新建fans分组"""
        return self.db.execute('insert into t_fans_group (name, aid) values (%s, %s)', name, aid)

    def change_fans_group(self, fans_id, group):
        """修改fans分组"""
        self.db.execute('update t_fans set group_id = %s, group_name = %s where id = %s', group.id, group.name, fans_id)

    def get_fans_group(self, aid):
        """获取账号所有的粉丝分组"""
        return self.db.query('select * from t_fans_group where aid = %s', aid)

    def get_fans_by_id(self, fans_id):
        """根据id获取粉丝对象"""
        return self.db.get('select * from t_fans where id = %s limit 1', fans_id)

    def get_fans_by_openid(self, openid):
        """根据openid获取粉丝"""
        return self.db.get('select * from t_fans where openid = %s limit 1', openid)

    def get_fans_by_openid_aid(self, openid, aid):
        """根据openid和aid获取粉丝"""
        return self.db.get('select * from t_fans where openid = %s and aid = %s limit 1', openid, aid)

    def get_fans_count(self, aid, group_id):
        """获取粉丝数量"""
        if group_id:
            return self.db.get('select count(*) as count from t_fans where aid = %s and group_id = %s',
                               aid, group_id)['count']
        return self.db.get('select count(*) as count from t_fans where aid = %s', aid)['count']

    def save_single_fans(self, user, aid):
        """添加单个粉丝用户信息"""
        self.db.execute('insert into t_fans (date, openid, nickname, sex, country, province, city, avatar, '
                        'subscribe_time, language, aid) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        user['openid'], user['nickname'], user['sex'], user['country'], user['province'],
                        user['city'], user['headimgurl'], datetime.datetime.fromtimestamp(int(user['subscribe_time'])),
                        user['language'], aid)

    def save_single_fans_without_info(self, aid, openid):
        self.db.execute('insert into t_fans (date, openid, nickname, subscribe_time, aid) values (NOW(), %s, %s, '
                        'NOW(), %s)', openid, openid, aid)

    def save_fans(self, users, aid):
        """将粉丝插入数据库"""
        print 'FansManager.add_fans start...'
        for user in users:
            print user
            self.save_single_fans(user, aid)
        print 'FansManager.add_fans end...'

    def unsubscribe_fans(self, openid, aid):
        """粉丝取消关注，更新状态"""
        self.db.execute('update t_fans set status = 0 where openid = %s and aid = %s', openid, aid)

    def re_subscribe_fans(self, openid, aid):
        """粉丝重新关注，更新状态"""
        self.db.execute('update t_fans set status = 1, date = %s, subscribe_time = %s where openid = %s and aid = %s',
                        datetime.datetime.now(), datetime.datetime.now(), openid, aid)


class MessageManager(Base):
    def get_message_by_openid_aid(self, aid, openid, start, end):
        """获取跟某个用户之间的消息列表"""
        return self.db.query('select * from t_message where openid = %s and aid = %s order by id desc limit %s, %s',
                             openid, aid, int(start), int(end))

    def get_message_by_aid(self, aid, start, end):
        return self.db.query('select * from t_message where aid = %s group by openid '
                             'order by id desc limit %s, %s', aid, int(start), int(end))

    def get_message_count_by_aid_openid(self, aid, openid):
        """获取公众号跟某个粉丝之间的消息数量"""
        return self.db.get('select count(*) as count from t_message where aid = %s and openid = %s',
                           aid, openid)['count']

    def get_message_count_by_aid(self, aid):
        return self.db.get('select count(distinct openid) as count from t_message where aid = %s', aid)['count']

    def save_message(self, content, openid, aid):
        """发送消息后保存到数据库"""
        self.db.execute('insert into t_message (type, create_time, outgoing, content, openid, aid) '
                        'values (1, NOW(), 1, %s, %s, %s)', content, openid, aid)

    def receive_text_message(self, message, aid):
        """接收用户发来的文本消息，保存到数据库"""
        openid = message['FromUserName']
        content = message['Content']
        create_time = message['CreateTime']
        msg_id = message['MsgId']
        self.db.execute('insert into t_message (type, create_time, message_id, content, status, openid, aid)'
                        ' values (%s, %s, %s, %s, %s, %s, %s)', 'text',
                        datetime.datetime.fromtimestamp(int(create_time)), msg_id, content, 0, openid, aid)

    def receive_image_message(self, message, aid):
        """接收用户发送的图片消息"""
        openid = message['FromUserName']
        url = message['PicUrl']
        create_time = message['CreateTime']
        msg_id = message['MsgId']
        media_id = message['MediaId']
        self.db.execute('insert into t_message (type, create_time, message_id, url, media_id, status, openid, aid) '
                        'values (%s, %s, %s, %s, %s, %s, %s, %s)', 'image',
                        datetime.datetime.fromtimestamp(int(create_time)), msg_id, url, media_id, 0, openid, aid)

    def receive_voice_message(self, message, aid):
        """接收用户发送的语音消息"""
        openid = message['FromUserName']
        create_time = message['CreateTime']
        msg_id = message['MsgId']
        media_id = message['MediaId']
        msg_format = message['Format']
        self.db.execute('insert into t_message (type, create_time, message_id, media_id, format, status, openid, aid) '
                        'values (%s, %s, %s, %s, %s, %s, %s, %s)', 'voice',
                        datetime.datetime.fromtimestamp(int(create_time)), msg_id, media_id, msg_format, 0, openid, aid)

    def receive_video_message(self, message, aid):
        """接收用户发送的视频消息"""
        openid = message['FromUserName']
        create_time = message['CreateTime']
        msg_id = message['MsgId']
        media_id = message['MediaId']
        self.db.execute('insert into t_message (type, create_time, message_id, media_id, status, openid, aid) '
                        'values (%s, %s, %s, %s, %s, %s, %s)', 'video',
                        datetime.datetime.fromtimestamp(int(create_time)), msg_id, media_id, 0, openid, aid)

    def receive_location_message(self, message, aid):
        """接收用户发送的位置消息"""
        openid = message['FromUserName']
        create_time = message['CreateTime']
        msg_id = message['MsgId']
        x = message['Location_X']
        y = message['Location_Y']
        scale = message['Scale']
        label = message['Label']
        self.db.execute(
            'insert into t_message (type, create_time, message_id, x, y, scale, label, status, openid, aid) '
            'values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', 'location',
            datetime.datetime.fromtimestamp(int(create_time)), msg_id, x, y, scale, label, 0, openid, aid)

    def receive_link_message(self, message, aid):
        """接收用户发送的链接消息"""
        openid = message['FromUserName']
        create_time = message['CreateTime']
        msg_id = message['MsgId']
        url = message['Url']
        self.db.execute('insert into t_message (type, create_time, message_id, url, status, openid, aid) '
                        'values (%s, %s, %s, %s, %s, %s, %s)', 'video',
                        datetime.datetime.fromtimestamp(int(create_time)), msg_id, url, 0, openid, aid)


class ArticleManager(Base):
    def get_auto_response(self, aid):
        """获取公众账号的关注时的回复信息"""
        return self.db.get('select * from t_article where aid = %s and auto_response = 1', aid)

    def save_auto_response(self, aid, slug, content, _type):
        """保存自动回复信息"""
        self.db.execute('insert into t_article (slug, content, aid, auto_response, type) values '
                        '(%s, %s, %s, %s, %s)', slug, content, aid, 1, _type)

    def exists_article(self, slug):
        """查询slug是否被占用"""
        return self.db.get('select count(*) as count from t_article where slug = %s', slug)['count']

    def save_article(self, slug, title, content, aid):
        """保存文章到数据库"""
        self.db.execute('insert into t_article (date, slug, title, content, aid) values (NOW(), %s, %s, %s, %s)',
                        slug, title, content, aid)

    def get_article(self, aid, start, end):
        """从数据库获取文章列表"""
        return self.db.query('select * from t_article where aid = %s order by id desc limit %s, %s',
                             aid, int(start), int(end))

    def get_article_count_by_aid(self, aid):
        """"获取文章总数量"""
        return self.db.get('select count(*) as count from t_article where aid = %s', aid)['count']

    def get_article_by_slug(self, slug):
        """根据文章id获取文章"""
        return self.db.get('select * from t_article where slug = %s', slug)

    def update_article(self, slug, title, content):
        """更新文章内容"""
        self.db.execute('update t_article set title = %s, content = %s where slug = %s', title, content, slug)

    def delete_article(self, slug):
        """删除文章"""
        self.db.execute('delete from t_article where slug = %s', slug)


class MenuManager(Base):
    def get_main_menu_list(self, aid):
        """"获取保存的自定义菜单的主菜单"""
        return self.db.query('select * from t_menu where aid = %s and first = 1 order by id', aid)

    def get_sub_menu_list(self, aid, parent_id):
        """获取保存的自定义菜单的二级菜单"""
        return self.db.query('select * from t_menu where aid = %s and second = 1 and parent_id = %s order by id', aid,
                             parent_id)

    def save_main_menu_item(self, aid, name):
        """保存自定义菜单中的主菜单，并返回id"""
        return self.db.execute('insert into t_menu (date, name, first, second, aid) values (NOW(), %s, %s, %s, %s)',
                               name, 1, 0, aid)

    def save_main_menu_item_response(self, aid, name, t, url, auto_id, mkey):
        """保存作为回复的一级菜单"""
        return self.db.execute('insert into t_menu (date, name, first, second, type, url, auto_id, parent_id, '
                               'mkey, aid) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)', name, 1, 0, t,
                               url, auto_id, 0, mkey, aid)

    def save_sub_menu_item(self, aid, name, t, url, auto_id, parent_id, mkey):
        """保存自定菜单中的二级菜单"""
        return self.db.execute('insert into t_menu (date, name, first, second, type, url, auto_id, parent_id, '
                               'mkey, aid) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)', name, 0, 1, t,
                               url, auto_id, parent_id, mkey, aid)

    def truncate_account_menu(self, aid):
        """清空账号已定义的菜单记录"""
        self.db.execute('delete from t_menu where aid = %s', aid)


class ImageArticleManager(Base):
    def get_image_article_by_id(self, _id):
        """根据id获取单条图文"""
        return self.db.get('select * from t_image_article where id = %s', int(_id))

    def get_image_article_by_id_list(self, id_list):
        """根据多个id获取图文消息"""
        rows = []
        for _id in id_list:
            rows.append(self.db.get('select * from t_image_article where id = %s', _id))
        return rows

    def list_single_image_article(self, aid, start, end):
        """获取单条图文列表"""
        return self.db.query('select * from t_image_article where aid = %s and type = 0 order by id desc limit %s, %s',
                             aid, int(start), int(end))

    def get_image_article_count_by_aid(self, aid):
        """"获取单条图文总数量"""
        return self.db.get('select count(*) as count from t_image_article where aid = %s and type = 0', aid)['count']

    def list_group_image_article(self, aid, start, end):
        """获取多条图文列表"""
        return self.db.query('select * from t_image_article_group where aid = %s order by id desc limit %s, %s',
                             aid, int(start), int(end))

    def get_image_article_group_count_by_aid(self, aid):
        """"获取多条图文总数量"""
        return self.db.get('select count(*) as count from t_image_article_group where aid = %s', aid)['count']

    def save_single_image_article(self, title, summary, link, image, aid):
        """保存到条图文"""
        self.db.execute('insert into t_image_article (date, title, link, summary, image, aid) '
                        'values (NOW(), %s, %s, %s, %s, %s)', title, link, summary, image, aid)

    def update_single_image_article(self, title, summary, link, image, iid, aid):
        """更新单条图文消息"""
        self.db.execute('update t_image_article set title = %s, summary = %s, link = %s, image = %s where aid = %s '
                        'and id = %s', title, summary, link, image, aid, iid)

    def save_single_image_article_with_type(self, title, summary, link, image, aid):
        """保存到条图文"""
        return self.db.execute('insert into t_image_article (date, title, link, summary, image, type, aid) '
                               'values (NOW(), %s, %s, %s, %s, 1, %s)', title, link, summary, image, aid)

    def list_multi_image_article(self, aid, start, end):
        """获取多条图文消息列表"""
        return self.db.query('select * from t_image_article_group where aid = %s order by id desc limit %s, %s',
                             aid, int(start), int(end))

    def save_multi_image_article(self, id1, id2, id3, id4, id5, title, aid):
        """"保存多条图文消息"""
        return self.db.execute('insert into t_image_article_group (date, id1, id2, id3, id4, id5, title, aid) '
                               'values (NOW(), %s, %s, %s, %s, %s, %s, %s)', id1, id2, id3, id4, id5, title, aid)

    def update_multi_image_article(self, id1, id2, id3, id4, id5, title, _id):
        self.db.execute('update t_image_article_group set id1 = %s, id2 = %s, id3 = %s, id4 = %s, id5 = %s, '
                        'title = %s where id = %s', id1, id2, id3, id4, id5, title, _id)

    def get_multi_image_article_by_id(self, _id):
        """根据id获取image_article_group"""
        return self.db.get('select * from t_image_article_group where id = %s', _id)

    def remove_single_image_article(self, _id, aid):
        """根据id删除image_article"""
        self.db.execute('delete from t_image_article where id = %s and aid = %s', int(_id), aid)

    def remove_image_article_grouo(self, _id, aid):
        """根据id删除image_article_group"""
        self.db.execute('delete from t_image_article where group_id = %s and aid = %s', int(_id), aid)
        self.db.execute('delete from t_image_article_group where id = %s and aid = %s', int(_id), aid)


class AutoManager(Base):
    def get_auto_by_id(self, _id):
        """根据id获取自动回复"""
        return self.db.get('select * from t_auto where id = %s', _id)

    def get_auto_by_key(self, mkey):
        """根据key获取自动回复"""
        return self.db.get('select * from t_auto where mkey = %s', mkey)

    def get_follow_auto(self, aid):
        """获取账号设置的关注自动回复信息"""
        return self.db.get('select * from t_auto where aid = %s and re_time = %s', aid, 'follow')

    def save_text_auto(self, aid, content):
        """保存文本回复信息"""
        self.db.execute('insert into t_auto (date, aid, type, re_time, re_content) values (NOW(), %s, %s, %s, %s)',
                        aid, 'text', 'follow', content)

    def save_text_auto_response(self, aid, re_type, content, mkey):
        """保存菜单中的文字自动回复，并返回该条目的id"""
        return self.db.execute('insert into t_auto (date, aid, type, re_time, re_content, mkey) '
                               'values (NOW(), %s, %s, %s, %s, %s)', aid, re_type, 'click', content, mkey)

    def save_card_auto_response(self, aid, mkey):
        """保存菜单中的会员卡回复，并返回该条目的id"""
        return self.db.execute('insert into t_auto (date, aid, type, re_time, mkey) '
                               'values (NOW(), %s, %s, %s, %s)', aid, 'card', 'click', mkey)

    def save_image_article_auto(self, aid, re_type, re_img_art_id):
        """保存菜单中的图文自动，并返回该条目的id"""
        return self.db.execute('insert into t_auto (date, aid, type, re_time, re_img_art_id) '
                               'values (NOW(), %s, %s, %s, %s)', aid, re_type, 'follow', re_img_art_id)

    def save_image_article_auto_response(self, aid, re_type, re_img_art_id, mkey):
        """保存菜单中的图文自动，并返回该条目的id"""
        return self.db.execute('insert into t_auto (date, aid, type, re_time, re_img_art_id, mkey) '
                               'values (NOW(), %s, %s, %s, %s, %s)', aid, re_type, 'click', re_img_art_id, mkey)

    def truncate_account_menu_auto(self, aid):
        """清空账号与自定义菜单相关的自动回复"""
        self.db.execute('delete from t_auto where aid = %s and mkey is not null and re_time = %s', aid, 'click')

    def remove_follow_auto_message(self, aid):
        """删除已经保存的关注自动回复"""
        self.db.execute('delete from t_auto where aid = %s and re_time = %s', aid, 'follow')


class FormManager(Base):
    """表单管理类"""

    def get_form_by_fid(self, fid):
        """根据fid获取表单"""
        return self.db.get('select * from t_form where fid = %s', fid)

    def save_form(self, name, fid, aid, content):
        """保存自定义表单"""
        self.db.execute('insert into t_form (name, date, fid, content, aid) values (%s, now(), %s, %s, %s)', name, fid,
                        content, aid)

    def get_form_list_by_aid(self, aid):
        """根据aid获取自定义表单列表"""
        return self.db.query('select * from t_form where aid = %s order by id desc', aid)

    def save_input_to_form_content(self, fid, content):
        """将数据存储到表"""
        self.db.execute('insert into t_form_content (date, fid, content) values (NOW(), %s, %s)', fid, content)

    def list_form_content_by_fid(self, fid):
        """查询填写的表单列表"""
        return self.db.query('select * from t_form_content where fid = %s order by id desc', fid)


class CardManager(Base):
    """"会员卡管理"""

    def save_card(self, aid, cid, register, name, mobile, address, phone, about, cover, sex, birthday):
        """公众号创建会员卡"""
        self.db.execute(
            'insert into t_card (date, aid, cid, register, name, mobile, address, phone, about, cover, sex, birthday) '
            'values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', aid, cid, register, name, mobile, address,
            phone, about, cover, sex, birthday)

    def update_card(self, cid, register, name, mobile, address, phone, about, cover, sex, birthday):
        """公众号创建会员卡"""
        self.db.execute('update t_card set register = %s, name = %s, mobile = %s, address = %s, phone = %s, about = %s,'
                        ' cover = %s, sex = %s, birthday = %s where cid = %s', register, name, mobile, address, phone,
                        about, cover, sex, birthday, cid)

    def save_member(self, aid, cid, num, openid, name, mobile, address, sex, birthday):
        """保存用户的会员卡信息"""
        self.db.execute('insert into t_card_member (date, aid, cid, num, openid, name, mobile, address, sex, birthday) '
                        'values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)', aid, cid, num, openid, name, mobile,
                        address, sex, birthday)

    def get_user_card_info(self, cid, openid):
        """用户是否有会员卡"""
        return self.db.get('select * from t_card_member where cid = %s and openid = %s', cid, openid)

    def list_card_member(self, aid, cid, group_id, start, end):
        """列出公众号的所有会员信息"""
        if not group_id:
            return self.db.query('select * from t_card_member where aid = %s and cid = %s order by id desc limit %s, '
                                 '%s', aid, cid, start, end)
        return self.db.query('select * from t_card_member where aid = %s and cid = %s and group_id = %s order by id '
                             'desc limit %s, %s', aid, cid, group_id, start, end)

    def get_card_member_count(self, aid, cid, group_id):
        """公众号所有会员数量"""
        if not group_id:
            return self.db.get('select count(*) as count from t_card_member where aid = %s and cid = %s', aid, cid)[
                'count']
        return self.db.get('select count(*) as count from t_card_member where aid = %s and cid = %s and group_id = %s',
                           aid, cid, group_id)['count']

    def get_card_by_cid(self, cid):
        """根据会员卡id获取会员卡"""
        return self.db.get('select * from t_card where cid = %s', cid)

    def get_card_by_aid(self, aid):
        """获取公众账号的会员卡信息"""
        return self.db.get('select * from t_card where aid = %s', aid)

    def get_card_member_by_id(self, aid, _id):
        """获取会员"""
        return self.db.get('select * from t_card_member where aid = %s and id = %s', aid, _id)

    def get_card_member_by_openid(self, aid, openid):
        """根据openid获取会员卡信息"""
        return self.db.get('select * from t_card_member where aid = %s and openid = %s', aid, openid)

    def new_card_member_group(self, aid, name):
        """新建会员分组"""
        return self.db.execute('insert into t_card_member_group (name, aid) values (%s, %s)', name, aid)

    def get_member_group_by_id(self, aid, _id):
        """获取会员分组"""
        return self.db.get('select * from t_card_member_group where aid = %s and id = %s', aid, _id)

    def get_member_group_by_name(self, aid, name):
        return self.db.get('select * from t_card_member_group where aid = %s and name = %s', aid, name)

    def change_member_group(self, member_id, group):
        """修改会员分组"""
        self.db.execute('update t_card_member set group_id = %s, group_name = %s where id = %s', group.id,
                        group.name, member_id)

    def remove_card_member_group(self, group_id):
        """移除会员分组"""
        self.db.execute('update t_card_member set group_id = 0, group_name = null where group_id = %s', group_id)
        self.db.execute('delete from t_card_member_group where id = %s', group_id)

    def list_member_groups(self, aid):
        return self.db.query('select * from t_card_member_group where aid = %s', aid)

    def save_card_rule(self, aid, follow, time, message, share):
        """会员积分规则"""
        self.db.execute('insert into t_card_rule (date, aid, follow, time, message, share) values '
                        '(NOW(), %s, %s, %s, %s, %s)', aid, follow, time, message, share)

    def update_card_rule(self, aid, follow, time, message, share):
        self.db.execute('update t_card_rule set follow = %s, time = %s, message = %s, share = %s where aid = %s',
                        follow, time, message, share, aid)

    def get_account_card_rule(self, aid):
        return self.db.get('select * from t_card_rule where aid = %s', aid)

    def list_history(self, aid, start, size):
        return self.db.query('select * from t_card_history where aid = %s order by id desc limit %s, %s', aid, start,
                             size)

    def history_count(self, aid):
        return self.db.get('select count(*) as count from t_card_history where aid = %s', aid)['count']

    def new_history(self, aid, openid, type, point, card_num):
        self.db.execute('insert into t_card_history (date, aid, openid, type, point, card_num) values (NOW(), %s, %s,'
                        '%s, %s, %s)', aid, openid, type, point, card_num)

    def update_history_by_type(self, openid, point, type):
        self.db.execute('update t_card_history set point = %s where openid = %s and type = %s', point, openid, type)

    def get_history_by_type(self, openid, aid, type):
        return self.db.get('select * from t_card_history where openid = %s and aid = %s and type = %s', openid, aid,
                           type)

    def update_all_member_point(self):
        self.db.execute('update t_card_member m set m.point = (select sum(h.point) from t_card_history h '
                        'where m.openid = h.openid)')

    def update_member_point_by_openid(self, openid):
        self.db.execute('update t_card_member m set m.point = (select sum(h.point) from t_card_history h '
                        'where m.openid = h.openid) where m.openid = %s', openid)

    def get_history_by_openid(self, aid, openid):
        return self.db.query('select * from t_card_history where openid = %s and aid = %s', openid, aid)


class ImpactManager(Base):
    """用户印象管理"""

    def save_impact(self, aid, name, num):
        """公众号创建印象条目"""
        self.db.execute('insert into t_impact (date, aid, name, num) values (NOW(), %s, %s, %s)', aid, name, num)

    def vote_to_impact(self, _id):
        """用户为印象投票"""
        self.db.execute('update t_impact set num = num + 1 where id = %s', _id)

    def get_impact_by_id(self, _id):
        """根据id获取印象"""
        return self.db.get('select * from t_impact where id = %s', _id)

    def list_impact(self, aid):
        """公众号列出印象条目"""
        return self.db.query('select * from t_impact where aid = %s order by num desc', aid)

    def truncate_impacts(self, aid):
        """清空添加的印象"""
        self.db.execute('delete from t_impact where aid = %s', aid)

    def total_impact_num(self, aid):
        """印象总数量"""
        return self.db.get('select sum(num) as num from t_impact where aid = %s', aid)['num']


class AutoKeywordManager(Base):
    """关键字回复管理"""

    def save_content_auto_keyword(self, word, re_content, aid, wild):
        """文本回复"""
        self.db.execute('insert into t_auto_keyword (word, re_type, re_content, aid, wild) values (%s, %s, %s, %s, %s)',
                        word, 'text', re_content, aid, wild)

    def save_image_art_auto_keyword(self, word, re_img_art_id, aid, wild):
        """图文消息回复"""
        self.db.execute(
            'insert into t_auto_keyword (word, re_type, re_img_art_id, aid, wild) values (%s, %s, %s, %s, %s)',
            word, 'single', re_img_art_id, aid, wild)

    def save_image_art_group_auto_keyword(self, word, re_img_art_id, aid, wild):
        """多条图文消息回复"""
        self.db.execute(
            'insert into t_auto_keyword (word, re_type, re_img_art_id, aid, wild) values (%s, %s, %s, %s, %s)',
            word, 'multi', re_img_art_id, aid, wild)

    def list_auto(self, aid):
        """查询关键字回复列表"""
        return self.db.query('select * from t_auto_keyword where aid = %s order by id desc', aid)

    def truncate_auto(self, aid):
        """清空记录"""
        self.db.execute('delete from t_auto_keyword where aid = %s', aid)

    def get_auto_by_word(self, aid, word):
        """获取记录"""
        _list = self.db.query('select * from t_auto_keyword where aid = %s and word = %s and wild = 0 order by rand()',
                              aid, word)
        if _list:
            return _list[0]
        return None

    def list_auto_by_wild(self, aid):
        """获取所有模糊匹配的回复列表"""
        _list = self.db.query('select * from t_auto_keyword where aid = %s and wild = 1 order by rand()', aid)
        return _list


class SiteManager(Base):
    """微官网"""

    def initial(self, aid):
        self.db.execute('delete from t_site where aid = %s', aid)
        self.db.execute('delete from t_site_ul where aid = %s', aid)

    def save_site(self, aid, title, phone, img1, img2, img3, img4, img5):
        self.db.execute('insert into t_site (aid, title, phone, img1, img2, img3, img4, img5) values (%s, %s, %s, '
                        '%s, %s, %s, %s, %s)', aid, title, phone, img1, img2, img3, img4, img5)

    def save_site_ul(self, aid, name, icon, link):
        self.db.execute('insert into t_site_ul (aid, name, icon, url) values (%s, %s, %s, %s)', aid, name, icon, link)

    def get_site(self, aid):
        return self.db.get('select * from t_site where aid = %s', aid)

    def get_site_ul(self, aid):
        return self.db.query('select * from t_site_ul where aid = %s', aid)


class EventManager(Base):
    """刮刮卡"""

    def get_event(self, aid, type):
        return self.db.get('select * from t_event where aid = %s and type = %s', aid, type)

    def save_event(self, start, end, length, aid, prize_1, prize_2, prize_3, num_1, num_2, num_3, num_sum, active,
                   times, description, _type, member):
        self.db.execute('insert into t_event (date, start, end, length, aid, prize_1, prize_2, prize_3, num_1,'
                        ' num_2, num_3, num_sum, active, times, description, type, member) values (NOW(), %s, %s, %s, '
                        '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', start, end, length, aid, prize_1,
                        prize_2, prize_3, num_1, num_2, num_3, num_sum, active, times, description, _type, member)

    def update_event(self, start, end, length, aid, prize_1, prize_2, prize_3, num_1, num_2, num_3, num_sum, active,
                     times, description, _type, member):
        self.db.execute('update t_event set start = %s, end = %s, length = %s, prize_1 = %s, prize_2 = %s, '
                        'prize_3 = %s, num_1 = %s, num_2 = %s, num_3 = %s, num_sum = %s, active = %s, times = %s, '
                        'description = %s, member = %s where aid = %s and type = %s', start, end, length, prize_1,
                        prize_2, prize_3, num_1, num_2, num_3, num_sum, active, times, description, member, aid, _type)

    def change_status(self, aid, active, type):
        self.db.execute('update t_event set active = %s where aid = %s and type = %s', active, aid, type)

    def get_event_num_by_openid(self, openid, aid, type):
        return self.db.get('select count(*) as count from t_event_result where openid = %s and aid = %s and type = %s',
                           openid, aid, type)['count']

    def get_hit_event_num_by_openid(self, openid, aid, type):
        return self.db.get('select count(*) as count from t_event_result where openid = %s and aid = %s and type = %s'
                           ' and prize > 0', openid, aid, type)['count']

    def hit_num_since_date(self, aid, since, type):
        return self.db.get('select count(*) as count from t_event_result where date > %s and aid = %s and type = %s'
                           ' and prize > 0', since, aid, type)['count']

    def hit_num_by_pirze(self, aid, prize, type):
        return self.db.get('select count(*) as count from t_event_result where aid = %s and prize = %s and type = %s',
                           aid, prize, type)['count']

    def save_event_result(self, aid, openid, prize, sn, type):
        return self.db.execute(
            'insert into t_event_result (date, aid, openid, prize, sn, type) values (NOW(), %s, %s, %s, %s, %s)',
            aid, openid, prize, sn, type)

    def update_event_phone(self, openid, sn, _id, phone, type):
        self.db.execute('update t_event_result set phone = %s where openid = %s and sn = %s and id = %s and type = %s',
                        phone, openid, sn, _id, type)

    def list_event_history(self, aid, start, size, type):
        return self.db.query('select * from t_event_result where aid = %s and type = %s order by id desc limit %s, %s',
                             aid, type, start, size)

    def event_history_count(self, aid, type):
        return self.db.get(
            'select count(*) as count from t_event_result where aid = %s and type = %s', aid, type)['count']


class AnalyticsManager(Base):
    """统计"""

    def save_share_history(self, openid, slug, success, type, aid):
        self.db.execute('insert into t_share_history (date, slug, openid, success, type, aid) values (NOW(), %s, %s, '
                        '%s, %s, %s)', slug, openid, success, type, aid)

    def list_share_history(self, aid, start, size):
        return self.db.query('select * from t_share_history where aid = %s order by id desc limit %s, %s', aid, start,
                             size)

    def count_share_by_openid(self, aid, openid):
        return self.db.get('select count(*) as count from t_share_history where aid = %s and openid = %s and '
                           'success = 1', aid, openid)['count']

    def save_view_history(self, aid, slug, openid):
        self.db.execute('insert into t_view_history (date, aid, slug, openid) values (NOW(), %s, %s, %s)',
                        aid, slug, openid)

    def total_view_num_today(self, aid):
        now = datetime.now()
        start = datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0)
        return self.db.get('select count(*) as count from t_view_history where aid = %s and date > %s', aid, start)[
            'count']

    def total_view_num(self, aid):
        return self.db.get('select count(*) as count from t_view_history where aid = %s', aid)['count']

    def total_fans_num(self, aid):
        return self.db.get('select count(*) as count from t_fans where aid = %s', aid)['count']

    def total_fans_num_today(self, aid):
        return self.db.get('select count(*) as count ')


class TemplateManager(Base):
    def save_template(self, aid, title, slug, type, thumb):
        self.db.execute(
            'insert into t_template (date, aid, slug, title, type, thumb) values (NOW(), %s, %s, %s, %s, %s)',
            aid, slug, title, type, thumb)

    def save_template_list(self, slug, title, link, thumb, rank):
        self.db.execute('insert into t_template_list (slug, title, link, thumb, rank) values (%s, %s, %s, %s, %s)',
                        slug, title, link, thumb, rank)

    def list_template(self, aid):
        return self.db.query('select * from t_template where aid = %s order by id desc', aid)


class CanyinManager(Base):
    def save_dish(self, aid, name, price, unit, img, cate_id, special, special_price, rank, count, hot, description):
        self.db.execute(
            'insert into t_canyin_dish (date, aid, name, price, unit, img, cate_id, special, special_price, '
            'rank, num, hot, description) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'
            ' %s, %s)', aid, name, price, unit, img, cate_id, special, special_price, rank, count, hot, description)

    def update_dish(self, did, aid, name, price, unit, img, cate_id, special, special_price, rank, count,
                    hot, description):
        self.db.execute('update t_canyin_dish set name = %s, price = %s, unit = %s, img = %s, cate_id = %s, '
                        'special = %s, special_price = %s, rank = %s, num = %s, hot = %s, '
                        'description = %s where aid = %s and id = %s', name, price, unit, img, cate_id, special,
                        special_price, rank, count, hot, description, aid, did)

    def delete_dish(self, aid, _id):
        self.db.execute('delete from t_canyin_dish where aid = %s and id = %s', aid, _id)

    def get_dish_by_id(self, aid, _id):
        return self.db.get('select * from t_canyin_dish where aid = %s and id = %s', aid, _id)

    def save_cate(self, aid, name, rank, _id):
        if not _id:
            self.db.execute('insert into t_canyin_cate (date, name, aid, rank) values (NOW(), %s, %s, %s)', name, aid,
                            rank)
        else:
            self.db.execute('update t_canyin_cate set name = %s, rank = %s where id = %s and aid = %s', name, rank, _id,
                            aid)

    def delete_cate(self, aid, _id):
        self.db.execute('delete from t_canyin_cate where id = %s and aid = %s', _id, aid)

    def list_cate(self, aid):
        return self.db.query('select * from t_canyin_cate where aid = %s order by rank desc', aid)

    def list_dish_by_cate(self, aid, cate_id):
        return self.db.query('select * from t_canyin_dish where cate_id = %s and aid = %s order by rank desc', cate_id,
                             aid)

    def list_all_dish(self, aid):
        return self.db.query('select * from t_canyin_dish where aid = %s order by rank desc', aid)

    def have_in(self, aid, dish_id, openid):
        return self.db.get('select count(*) as count from t_canyin_my where aid = %s and dish_id = %s and openid = %s',
                           aid, dish_id, openid)['count']

    def add_to_my(self, aid, openid, dish_id, cate_id):
        self.db.execute('insert into t_canyin_my (date, aid, openid, cate_id, dish_id, num) values '
                        '(NOW(), %s, %s, %s, %s, 1)', aid, openid, cate_id, dish_id)

    def increase_my_dish_num(self, dish_id):
        self.db.execute('update t_canyin_my set num = num + 1 where dish_id = %s', dish_id)

    def increase_dish_ordered_num(self, aid, dish_id):
        self.db.execute('update t_canyin_dish set num = num + 1 where id = %s and aid = %s', dish_id, aid)

    def decrease_dish_ordered_num(self, aid, dish_id):
        self.db.execute('update t_canyin_dish set num = num - 1 where id = %s and aid = %s', dish_id, aid)

    def list_my(self, openid, aid):
        return self.db.query('select * from t_canyin_my where openid = %s and aid = %s', openid, aid)

    def get_my_dish_by_dish_id(self, aid, openid, dish_id):
        return self.db.get('select * from t_canyin_my where aid = %s and openid = %s and dish_id = %s', aid, openid,
                           dish_id)

    def remove_my_dish(self, _id, openid):
        return self.db.execute('delete from t_canyin_my where openid = %s and dish_id = %s', openid, _id)

    def decrease_my_dish_num(self, openid, _id):
        self.db.execute('update t_canyin_my set num = num - 1 where openid = %s and dish_id = %s', openid, _id)

    def count_my_by_cate(self, aid, openid, cate_id):
        return self.db.get('select count(*) as count from t_canyin_my where aid = %s and openid = %s and cate_id = %s',
                           aid, openid, cate_id)['count']

    def remove_all_my_dish(self, aid, openid):
        self.db.execute('delete from t_canyin_my where aid = %s and openid = %s', aid, openid)

    def history_count(self, aid):
        return self.db.get('select count(*) as count from t_canyin_my where aid = %s', aid)['count']

    def history_list(self, aid, start, size):
        return self.db.query('select * from t_canyin_my where aid = %s order by id desc limit %s, %s', aid, start, size)