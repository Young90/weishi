#coding:utf-8
__author__ = 'young'

import math
import time
import string
from tornado.web import HTTPError, asynchronous
from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
import weishi.libs.image as image_util
from weishi.libs import wei_api
from weishi.libs import id_generator


class AccountBaseHandler(BaseHandler):
    """
    用户管理微信号的base handler
    用户进入/account/{aid}/*的页面，保证获取的access_token可用
    """

    account = None

    @authenticated
    @asynchronous
    def prepare(self):
        aid = self.request.uri.split('/')[2]
        if not aid:
            raise HTTPError(404)
            return
        account = self.db.get('select * from t_account where aid = %s', aid)
        if not account:
            raise HTTPError(404)
            return
        if account.user_id != self.current_user.id:
            raise HTTPError(403)
            return
        if not wei_api.access_token_available(account):
            wei_api.get_access_token(account, self._update_account_token)
        AccountBaseHandler.account = account

    def _update_account_token(self, account):
        """当access_token过期后，获取微信的access_token"""
        print 'account.py _update_account_token start...'
        self.account['access_token'] = account.access_token
        self.account['expires'] = account.expires
        self.db.execute('update t_account set access_token = %s, expires = %s where aid = %s',
                        self.account.access_token, self.account.expires, self.account.aid)
        print 'account.py _update_account_token end...'

    def _get_fans(self, start, end):
        """获取账号的所有粉丝"""
        return self.db.query('select * from t_fans where aid = %s limit %s, %s',
                             self.account.aid, start, end)

    def _get_fans_by_id(self, fans_id):
        """根据id获取粉丝对象"""
        return self.db.get('select * from t_fans where id = %s limit 1', fans_id)

    def _get_message_by_openid_aid(self, openid, start, end):
        """获取跟某个用户之间的消息列表"""
        return self.db.query('select * from t_message where openid = %s and aid = %s limit %s, %s',
                             openid, self.account.aid, start, end)

    def _get_auto_response(self):
        """获取公众账号的关注时的回复信息"""
        return self.db.get('select * from t_article where aid = %s and auto_response = 1', self.account.aid)

    def _save_auto_response(self, _slug, _content, _type):
        """保存自动回复信息"""
        self.db.execute('insert into t_article (slug, content, aid, auto_response, type) values '
                        '(%s, %s, %s, %s, %s)', _slug, _content, self.account.aid, 1, _type)

    def _exists_article(self, slug):
        """查询slug是否被占用"""
        return self.db.execute_rowcount('select count(*) from t_article where slug = %s', slug)


class AccountIndexHandler(AccountBaseHandler):
    """
    微信号管理的默认处理方法
    """

    def get(self, aid):
        print 'account.py index start...'
        self.render('account/index.html', account=self.account)
        print 'account.py index end...'


class AccountFansHandler(AccountBaseHandler):
    """
    查看公共账号的所有粉丝
    """

    def get(self, aid):
        print 'account.py fans_list start...'
        start = self.get_argument('start', 0)
        page_size = 10
        fans = self.db.query('select * from t_fans where aid = %s limit %s, %s', aid, start, page_size)
        total = self.db.execute_rowcount('select count(*) from t_fans where aid = %s', aid)
        total_page = math.ceil(float(total) / page_size)
        self.render('account/fans.html', fans=fans, account=self.account, total=total,
                    start=start, total_page=total_page, page_size=page_size)
        print 'account.py fans_list end...'


class MessageHandler(AccountBaseHandler):
    """
    与某个用户之间的消息列表.发送消息
    """

    def get(self, aid, fans_id):
        """与某个用户之间的消息列表"""
        fans = self._get_fans_by_id(fans_id)
        if not fans or fans.aid != self.account.aid:
            raise HTTPError(404).message(u'粉丝不存在')
            return
        start = self.get_argument('start', 0)
        page_size = 10
        messages = self._get_message_by_openid_aid(fans.openid, start, page_size)
        total = self.db.execute_rowcount('select count(*) from t_message where aid = %s and openid = %s',
                                         self.account.aid, fans.openid)
        total_page = math.ceil(float(total) / page_size)
        self.render('account/fans_message.html', fan=fans, messages=messages, account=self.account, total=total,
                    start=start, total_page=total_page, page_size=page_size)

    def post(self, *args, **kwargs):
        """给某个用户发送消息"""
        fans_id = self.get_argument('fans_id', 1)
        fans = self._get_fans_by_id(fans_id)
        result = {'r': 0}
        if not fans or fans.aid != self.account.aid:
            result['error'] = u'无效的粉丝id'
            self.write(result)
            return
        content = self.get_argument('content', None)
        if not content:
            result['error'] = u'内容不能为空'
            self.write(result)
        message = {'msgtype': 'text', 'touser': fans.openid, 'text': {'content': content}}
        wei_api.send_text_message(self.account, message, self._callback)

    def _callback(self, result, content, openid):
        self.write(result)
        self.finish()
        if result['r']:
            self.db.execute('insert into t_message (type, create_time, outgoing, content, openid, aid) '
                            'values (1, %s, 1, %s, %s, %s)', int(time.time()), content, openid, self.account.aid)


class MenuHandler(AccountBaseHandler):
    """自定义菜单"""

    def get(self, aid):
        """设置自定义菜单的页面"""
        menu = self.db.get('select * from t_menu where aid = %s', self.account.aid)
        self.render('account/menu.html', menu=menu, account=self.account)

    def post(self, *args, **kwargs):
        """设置自定义菜单"""
        menu = self.get_argument('menu', None)
        result = {'r': 0}
        if not menu:
            result['error'] = u'自定义菜单不能为空'
            self.write(result)
            return
        wei_api.set_menu(self.account, menu, self._call_back)
        self.write(result)

    def _call_back(self, result, menu):
        self.write(result)
        self.finish()
        if result['r']:
            self.db.execute('delete from t_menu where aid = %s', self.account.aid)
            self.db.execute('insert into t_menu (aid, menu) values (%s, %s)', self.account.aid, menu)


class AutoResponseHandler(AccountBaseHandler):
    """自动回复设置"""

    def get(self, aid):
        """查看已经设置的自动回复信息"""
        article = self._get_auto_response()
        self.render('account/auto_response.html', account=self.account, article=article)

    def post(self, *args, **kwargs):
        """修改自动回复信息"""
        result = {'r': 0}
        _content = self.get_argument('content', None)
        if not _content:
            result['error'] = u'内容不能为空'
            self.write(result)
        _type = self.get_argument('type', 'text')
        _slug = id_generator.id_gen(9, string.ascii_letters)
        while self._exists_article(_slug):
            _slug = id_generator.id_gen(9, string.ascii_letters)
        self._save_auto_response(_slug, _content, _type)
        result['r'] = 1
        self.write(result)


class UploadImageHandler(AccountBaseHandler):
    """上传图片接口，返回图片的url"""

    def post(self, *args, **kwargs):
        result = {'r': 0}
        try:
            file_body = self.request.files['file'][0]['body']
            url = image_util.upload(file_body, self.account.aid)
            if not url:
                result['error'] = u'上传出错'
                self.write(result)
                return
            result['r'] = 1
            self.write(result)
            return
        except KeyError:
            result['error'] = u'参数不正确或上传图片出错'
            self.write(result)
            return


class ImageListHandler(AccountBaseHandler):
    """图片列表接口，返回图片url列表"""

    def get(self, *args, **kwargs):
        print self.account.aid
        urls = image_util.list_all(self.account.aid)
        print len(urls)
        results = {'r': 1, 'count': len(urls), 'urls': urls}
        self.write(results)
        return


handlers = [
    (r'/account/([^/]+)', AccountIndexHandler),
    (r'/account/([^/]+)/fans', AccountFansHandler),
    (r'/account/([^/]+)/message/fans/([^/]+)', MessageHandler),
    (r'/account/([^/]+)/auto', AutoResponseHandler),
    (r'/account/([^/]+)/menu', MenuHandler),
    (r'/account/([^/]+)/image/upload', UploadImageHandler),
    (r'/account/([^/]+)/image/list', ImageListHandler)
]

