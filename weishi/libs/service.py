#coding:utf-8
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

    def get_user_by_email(self, email):
        """根据邮箱获取用户"""
        return self.db.get('select * from t_user where email = %s', email)

    def get_user_by_username(self, username):
        """根据用户名获取用户"""
        return self.db.get('select * from t_user where username = %s', username)


class AccountManager(Base):
    def create_account(self, wei_id, wei_name, wei_account, app_id, app_secret, token, aid, avatar, user_id):
        """添加微信公众账号"""
        self.db.execute("insert into t_account (date, wei_id, wei_name, wei_account, app_id, app_secret,"
                        " token, aid, avatar, user_id) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                        wei_id, wei_name, wei_account, app_id, app_secret, token, aid, avatar, user_id)

    def delete_account(self, aid, user_id):
        """删除公众账号"""
        self.db.excute('delete from t_account where aid = %s and user_id = %s', aid, user_id)

    def get_account_by_aid(self, aid):
        """根据aid获取公众账号"""
        return self.db.get('select * from t_account where aid = %s', aid)

    def update_account_token(self, account):
        """当access_token过期后，获取微信的access_token"""
        print 'AccountManager.update_account_token start...'
        self.db.execute('update t_account set access_token = %s, expires = %s where aid = %s',
                        account.access_token, account.expires, account.aid)
        print 'AccountManager.update_account_token end...'

    def check_account(self, aid):
        """经过微信服务器验证的，将checked设为1"""
        self.db.execute('update t_account set checked = 1 where aid = %s', aid)


class FansManager(Base):
    def get_fans(self, aid, start, end):
        """获取账号的粉丝"""
        return self.db.query('select * from t_fans where aid = %s limit %s, %s',
                             aid, start, end)

    def get_fans_by_id(self, fans_id):
        """根据id获取粉丝对象"""
        return self.db.get('select * from t_fans where id = %s limit 1', fans_id)

    def get_fans_count(self, aid):
        """获取粉丝数量"""
        return self.db.execute_rowcount('select count(*) from t_fans where aid = %s', aid)

    def save_single_fans(self, user, aid):
        """添加单个粉丝用户信息"""
        self.db.execute('insert into t_fans (date, openid, nickname, sex, country, province, city, avatar, '
                        'subscribe_time, language, aid) values (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        user['openid'], user['nickname'], user['sex'], user['country'], user['province'],
                        user['city'], user['headimgurl'], datetime.datetime.fromtimestamp(int(user['subscribe_time'])),
                        user['language'], aid)

    def save_fans(self, users, aid):
        """将粉丝插入数据库"""
        print 'FansManager.add_fans start...'
        for user in users:
            print user
            self.save_single_fans(user, aid)
        print 'FansManager.add_fans end...'


class MessageManager(Base):
    def get_message_by_openid_aid(self, aid, openid, start, end):
        """获取跟某个用户之间的消息列表"""
        return self.db.query('select * from t_message where openid = %s and aid = %s limit %s, %s',
                             openid, aid, start, end)

    def get_message_count_by_aid_openid(self, aid, openid):
        """获取公众号跟某个粉丝之间的消息数量"""
        return self.db.execute_rowcount('select count(*) from t_message where aid = %s and openid = %s',
                                        aid, openid)

    def save_message(self, content, openid, aid):
        """发送消息后保存到数据库"""
        self.db.execute('insert into t_message (type, create_time, outgoing, content, openid, aid) '
                        'values (1, %s, 1, %s, %s, %s)', int(time.time()), content, openid, aid)


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
        return self.db.execute_rowcount('select count(*) from t_article where slug = %s', slug)


class MenuManager(Base):
    def get_menu(self, aid):
        """"获取保存的自定义菜单"""
        return self.db.get('select * from t_menu where aid = %s', aid)

    def delete_menu(self, aid):
        """删除自定义菜单"""
        self.db.execute('delete from t_menu where aid = %s', aid)

    def save_menu(self, aid, menu):
        self.db.execute('insert into t_menu (aid, menu) values (%s, %s)', aid, menu)