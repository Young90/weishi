#coding:utf-8
__author__ = 'young'

import math
from tornado.web import HTTPError, asynchronous
from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
import weishi.libs.image as image_util
from weishi.libs import wei_api
from weishi.libs import key_util
from weishi.libs.service import FansManager, MessageManager, ArticleManager, AccountManager, \
    MenuManager, ImageArticleManager


class AccountBaseHandler(BaseHandler):
    """
    用户管理微信号的base handler
    用户进入/account/{aid}/*的页面，保证获取的access_token可用
    """

    account = None
    fans_manager = None
    message_manager = None
    article_manager = None
    account_manager = None
    menu_manager = None
    image_article_manager = None

    @authenticated
    @asynchronous
    def prepare(self):
        self.fans_manager = FansManager(self.db)
        self.message_manager = MessageManager(self.db)
        self.article_manager = ArticleManager(self.db)
        self.account_manager = AccountManager(self.db)
        self.menu_manager = MenuManager(self.db)
        self.image_article_manager = ImageArticleManager(self.db)

        aid = self.request.uri.split('/')[2]
        if not aid:
            raise HTTPError(404)
            return
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
            return
        if account.user_id != self.current_user.id:
            raise HTTPError(403)
            return
        if self.get_cookie('aid', None) != account.aid:
            self.set_cookie('aid', aid)
        if not wei_api.access_token_available(account):
            wei_api.get_access_token(account, self.account_manager.update_account_token)
            self.account = self.account_manager.get_account_by_aid(aid)
        AccountBaseHandler.account = account


class AccountIndexHandler(AccountBaseHandler):
    """
    微信号管理的默认处理方法
    """

    def get(self, aid):
        self.render('account/index.html', account=self.account, index='index')


class TuwenHandler(AccountBaseHandler):
    """
    微信号管理的默认处理方法
    """

    def get(self, aid):
        self.render('account/material_image_article_single.html', account=self.account, index='material', top='image_article')


class AccountFansHandler(AccountBaseHandler):
    """
    查看公共账号的所有粉丝
    """

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        fans = self.fans_manager.get_fans(aid, start, page_size)
        total = self.fans_manager.get_fans_count(aid)
        print 'total : %s' % total
        total_page = math.ceil(float(total) / page_size)
        print 'start : %s' % start
        print 'total_page : %s' % total_page
        self.render('account/fans.html', fans=fans, account=self.account, total=total,
                    start=int(start), total_page=total_page, page_size=page_size, prefix='/account/%s/fans' % aid,
                    index='fans')


class MessageHandler(AccountBaseHandler):
    """
    与某个用户之间的消息列表.发送消息
    """

    def get(self, aid, fans_id):
        """与某个用户之间的消息列表"""
        fans = self.fans_manager.get_fans_by_id(fans_id)
        if not fans or fans.aid != self.account.aid:
            raise HTTPError(404).message(u'粉丝不存在')
            return
        start = self.get_argument('start', 0)
        page_size = 10
        messages = self.message_manager.get_message_by_openid_aid(aid, fans.openid, start, page_size)
        total = self.message_manager.get_message_count_by_aid_openid(aid, fans.openid)
        total_page = math.ceil(float(total) / page_size)
        self.render('account/fans_message.html', fan=fans, messages=messages, account=self.account, total=total,
                    start=start, total_page=total_page, page_size=page_size, index='message')

    def post(self, *args, **kwargs):
        """给某个用户发送消息"""
        fans_id = self.get_argument('fans_id', 1)
        fans = self.fans_manager.get_fans_by_id(fans_id)
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
            self.message_manager.save_message(content, openid, self.account.aid)


class MenuHandler(AccountBaseHandler):
    """自定义菜单"""

    def get(self, aid):
        """设置自定义菜单的页面"""
        menu = self.menu_manager.get_menu(self.account.aid)
        self.render('account/menu.html', menu=menu, account=self.account, index='menu')

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
            self.menu_manager.delete_menu(self.account.aid)
            self.menu_manager.save_menu(self.account.aid, menu)


class AutoResponseHandler(AccountBaseHandler):
    """自动回复设置"""

    def get(self, aid):
        """查看已经设置的自动回复信息"""
        article = self.article_manager.get_auto_response(aid)
        self.render('account/auto_response.html', account=self.account, article=article, index='auto')

    def post(self, *args, **kwargs):
        """修改自动回复信息"""
        result = {'r': 0}
        _content = self.get_argument('content', None)
        if not _content:
            result['error'] = u'内容不能为空'
            self.write(result)
        _type = self.get_argument('type', 'text')
        _slug = key_util.generate_hexdigits_lower(8)
        while self.article_manager.exists_article(_slug):
            _slug = key_util.generate_hexdigits_lower(8)
        self.article_manager.save_auto_response(self.account.aid, _slug, _content, _type)
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
        urls = image_util.list_all(self.account.aid)
        results = {'r': 1, 'count': len(urls), 'urls': urls}
        self.write(results)
        self.finish()


handlers = [
    (r'/account/([^/]+)', AccountIndexHandler),
    (r'/account/([^/]+)/fans', AccountFansHandler),
    (r'/account/([^/]+)/message/fans/([^/]+)', MessageHandler),
    (r'/account/([^/]+)/auto', AutoResponseHandler),
    (r'/account/([^/]+)/menu', MenuHandler),
    (r'/account/([^/]+)/image/upload', UploadImageHandler),
    (r'/account/([^/]+)/image/list', ImageListHandler),
    (r'/account/([^/]+)/roll', ImageListHandler),
]

