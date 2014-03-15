#coding:utf-8
__author__ = 'young'

import math
import simplejson
import json
from tornado.web import HTTPError, asynchronous
from weishi.libs.decorators import authenticated
from weishi.libs.handler import BaseHandler
import weishi.libs.image as image_util
from weishi.libs import wei_api
from weishi.libs import key_util
from weishi.libs.service import FansManager, MessageManager, ArticleManager, AccountManager, \
    MenuManager, ImageArticleManager, AutoManager, FormManager, CardManager


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
    auto_manager = None
    form_manager = None
    card_manager = None

    @authenticated
    @asynchronous
    def prepare(self):
        self.fans_manager = FansManager(self.db)
        self.message_manager = MessageManager(self.db)
        self.article_manager = ArticleManager(self.db)
        self.account_manager = AccountManager(self.db)
        self.menu_manager = MenuManager(self.db)
        self.image_article_manager = ImageArticleManager(self.db)
        self.auto_manager = AutoManager(self.db)
        self.form_manager = FormManager(self.db)
        self.card_manager = CardManager(self.db)

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


class AccountFansHandler(AccountBaseHandler):
    """
    查看公共账号的所有粉丝
    """

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        fans = self.fans_manager.get_fans(aid, start, page_size)
        total = self.fans_manager.get_fans_count(aid)
        total_page = math.ceil(float(total) / page_size)
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
        menu = []
        main_menu = self.menu_manager.get_main_menu_list(aid)
        if not main_menu:
            self.render('account/menu.html', menu=None, account=self.account, index='menu')
            return
        for item in main_menu:
            if item.type and item.mkey:
                # 如果一级菜单没有子菜单
                if item.auto_id:
                    # 自动回复
                    auto = self.auto_manager.get_auto_by_id(item.auto_id)
                    p = {'name': item.name, 'type': auto.type,
                         'value': auto.re_content if auto.re_content else auto.re_img_art_id}
                else:
                    # url视图
                    p = {'name': item.name, 'type': 'link', 'value': item.url}
                menu.append(p)
            else:
                #如果有二级菜单，遍历所有的子菜单
                sub_menus = self.menu_manager.get_sub_menu_list(aid, item.id)
                p = {'name': item.name, 'type': 'button'}
                sub_buttons = []
                for sub in sub_menus:
                    if sub.type and sub.mkey and sub.auto_id:
                        # 如果二级菜单为点击事件，查询自动回复的类型和内容
                        auto = self.auto_manager.get_auto_by_id(sub.auto_id)
                        sub_button = {'name': sub.name, 'type': auto.type,
                                      'value': auto.re_content if auto.re_content else auto.re_img_art_id}
                    else:
                        # 如果二级菜单为url视图
                        sub_button = {'name': sub.name, 'type': 'link', 'value': sub.url}
                    sub_buttons.append(sub_button)
                p['sub_buttons'] = sub_buttons
                menu.append(p)
        self.render('account/menu.html', menu=menu, account=self.account, index='menu')

    def post(self, *args, **kwargs):
        """设置自定义菜单"""
        aid = self.account.aid
        params = self.get_argument('params', None)
        result = {'r': 1}
        button = []
        if not params:
            result['r'] = 0
            result['error'] = u'自定义菜单不能为空'
            self.write(result)
            self.finish()
            return
        params = simplejson.loads(params, encoding='utf-8')
        #先清空已保存的菜单记录
        self.menu_manager.truncate_account_menu(aid)
        #清空菜单相关的自动回复
        self.auto_manager.truncate_account_menu_auto(aid)
        for param in params:
            name = param['name']
            _type = param['type']
            if _type == 'button':
                _id = self.menu_manager.save_main_menu_item(aid, name)
                menu = {'name': name}
                sub_buttons = []
                for sub_button in param['sub_buttons']:
                    mkey = key_util.generate_hexdigits_lower(8)
                    sub_name = sub_button['name']
                    sub_type = sub_button['type']
                    sub_value = sub_button['value']
                    if sub_type == 'text':
                        auto_id = self.auto_manager.save_text_auto_response(aid=aid, content=sub_value, mkey=mkey,
                                                                            re_type='text')
                        self.menu_manager.save_sub_menu_item(aid=aid, name=sub_name, t='click', url=None,
                                                             auto_id=auto_id, parent_id=_id, mkey=mkey)
                        sub_menu = {'type': 'click', 'name': sub_name, 'key': mkey}
                    elif sub_type == 'single':
                        auto_id = self.auto_manager.save_image_article_auto_response(aid=aid, re_type='single',
                                                                                     re_img_art_id=sub_value, mkey=mkey)
                        self.menu_manager.save_sub_menu_item(aid=aid, name=sub_name, t='click', url=None,
                                                             auto_id=auto_id, parent_id=_id, mkey=mkey)
                        sub_menu = {'type': 'click', 'name': sub_name, 'key': mkey}
                    elif sub_type == 'multi':
                        auto_id = self.auto_manager.save_image_article_auto_response(aid=aid, re_type='multi',
                                                                                     re_img_art_id=sub_value, mkey=mkey)
                        self.menu_manager.save_sub_menu_item(aid=aid, name=sub_name, t='click', url=None,
                                                             auto_id=auto_id, parent_id=_id, mkey=mkey)
                        sub_menu = {'type': 'click', 'name': sub_name, 'key': mkey}
                    elif sub_type == 'link':
                        self.menu_manager.save_sub_menu_item(aid=aid, name=sub_name, t='view', url=sub_value, auto_id=0,
                                                             parent_id=_id, mkey=None)
                        sub_menu = {'type': 'view', 'name': sub_name, 'url': sub_value}
                    elif sub_type == 'card':
                        auto_id = self.auto_manager.save_card_auto_response(aid, mkey)
                        self.menu_manager.save_sub_menu_item(aid=aid, name=sub_name, t='card', url='', auto_id=auto_id,
                                                             parent_id=_id, mkey=mkey)
                        sub_menu = {'type': 'click', 'name': sub_name, 'key': mkey}
                    sub_buttons.append(sub_menu)
                menu['sub_button'] = sub_buttons
            elif _type == 'text':
                value = param['value']
                mkey = key_util.generate_hexdigits_lower(8)
                auto_id = self.auto_manager.save_text_auto_response(aid=aid, content=value, mkey=mkey, re_type='text')
                self.menu_manager.save_main_menu_item_response(aid=aid, name=name, t='click', url=None, auto_id=auto_id,
                                                               mkey=mkey)
                menu = {'type': 'click', 'name': name, 'key': mkey}
            elif _type == 'card':
                mkey = key_util.generate_hexdigits_lower(8)
                auto_id = self.auto_manager.save_card_auto_response(aid, mkey)
                self.menu_manager.save_main_menu_item_response(aid=aid, name=name, t='card', url='', auto_id=auto_id,
                                                               mkey=mkey)
                menu = {'type': 'click', 'name': name, 'key': mkey}
            elif _type == 'single':
                value = param['value']
                mkey = key_util.generate_hexdigits_lower(8)
                auto_id = self.auto_manager.save_image_article_auto_response(aid=aid, re_type='single',
                                                                             re_img_art_id=value, mkey=mkey)
                self.menu_manager.save_main_menu_item_response(aid=aid, name=name, t='click', url=None, auto_id=auto_id,
                                                               mkey=mkey)
                menu = {'type': 'click', 'name': name, 'key': mkey}
            elif _type == 'multi':
                value = param['value']
                mkey = key_util.generate_hexdigits_lower(8)
                auto_id = self.auto_manager.save_image_article_auto_response(aid=aid, re_type='multi',
                                                                             re_img_art_id=value, mkey=mkey)
                self.menu_manager.save_main_menu_item_response(aid=aid, name=name, t='click', url=None, auto_id=auto_id,
                                                               mkey=mkey)
                menu = {'type': 'click', 'name': name, 'key': mkey}
            elif _type == 'link':
                value = param['value']
                self.menu_manager.save_main_menu_item_response(aid=aid, name=name, t='view', url=value, auto_id=0,
                                                               mkey=None)
                menu = {'type': 'view', 'name': name, 'url': value}
            button.append(menu)
        button = {'button': button}
        wei_api.set_menu(self.account, button)
        self.write(result)
        self.finish()
        return


class AutoResponseHandler(AccountBaseHandler):
    """自动回复设置"""

    def get(self, aid):
        """查看已经设置的自动回复信息"""
        auto = self.auto_manager.get_follow_auto(aid)
        self.render('account/auto_response_follow.html', account=self.account, auto=auto, index='auto')

    def post(self, *args, **kwargs):
        """修改自动回复信息"""
        result = {'r': 1}
        _type = self.get_argument('type')
        _value = self.get_argument('value')
        if not _type or not _value:
            result['r'] = 0
            result['error'] = '无效的参数'
            self.write(result)
            self.finish()
        self.auto_manager.remove_follow_auto_message(self.account.aid)
        if _type == 'text':
            self.auto_manager.save_text_auto(self.account.aid, _value)
        elif _type == 'single':
            self.auto_manager.save_image_article_auto(self.account.aid, 'single', int(_value))
        elif _type == 'multi':
            self.auto_manager.save_image_article_auto(self.account.aid, 'multi', int(_value))
        self.write(result)
        self.finish()


class AutoResponseMessageHandler(AccountBaseHandler):
    """自动回复设置"""

    def get(self, aid):
        self.render('account/auto_response_message.html', account=self.account, index='auto')


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


class FormHandler(AccountBaseHandler):
    """自定义表单管理"""

    def get(self, aid):
        forms = self.form_manager.get_form_list_by_aid(self.account.aid)
        self.render('account/forms.html', account=self.account, index='form', forms=forms)


class FormDataHandler(AccountBaseHandler):
    """查看表单上数据"""

    def get(self, aid, fid):
        form = self.form_manager.get_form_by_fid(fid)
        if not form:
            raise HTTPError(404)
        if aid != form.aid:
            raise HTTPError(404)
        contents = json.loads(form.content)
        items = []
        for content in contents:
            items.append(content['name'])
        form_contents = self.form_manager.list_form_content_by_fid(fid)
        forms = []
        for form_content in form_contents:
            c = json.loads(form_content.content)
            c['date'] = form_content.date
            forms.append(c)
        self.render('account/form_data.html', account=self.account, index='form', contents=forms, items=items,
                    form=form)


class NewFormHandler(AccountBaseHandler):
    """自定义表单管理"""

    def get(self, aid):
        """返回页面"""
        self.render('account/forms_new.html', account=self.account, index='form')

    def post(self, *args, **kwargs):
        """创建表单"""
        result = {'r': 0}
        name = self.get_argument('name', None)
        params = self.get_argument('params', None)
        print name
        print params
        if not name or not params:
            result['error'] = '参数不正确'
            self.write(result)
            self.finish()
        self.form_manager.save_form(name, key_util.generate_hexdigits_lower(8), self.account.aid, params)
        result['r'] = 1
        result['aid'] = self.account.aid
        self.write(result)
        self.finish()


class CardHandler(AccountBaseHandler):
    """会员卡管理"""

    def get(self, aid):
        """
        如果还没有创建会员卡，则返回创建页面
        如果已经创建，列出会员信息
        """
        card = self.card_manager.get_card_by_aid(self.account.aid)
        if not card:
            self.render('account/card.html', account=self.account, index='card', card=None)
            return
        start = self.get_argument('start', 0)
        page_size = 20
        total = self.card_manager.get_card_member_count(self.account.aid, card.cid)
        total_page = math.ceil(float(total) / page_size)
        card_members = self.card_manager.list_card_member(aid, card.cid, int(start), int(start) + page_size)
        self.render('account/card.html', account=self.account, index='card', members=card_members, total=total,
                    total_page=total_page, page_size=page_size, start=start, card=card)
        return

    def post(self, *args, **kwargs):
        """提交会员卡创建信息"""
        register = self.get_argument('register', 0)
        name = self.get_argument('name', 0)
        mobile = self.get_argument('mobile', 0)
        address = self.get_argument('address', 0)
        phone = self.get_argument('phone', None)
        about = self.get_argument('about', None)
        cid = key_util.generate_hexdigits_lower(8)
        self.card_manager.save_card(self.account.aid, cid, register, name, mobile, address, phone, about)
        result = {'r': 1}
        self.write(result)
        self.finish()


handlers = [
    (r'/account/([^/]+)', AccountIndexHandler),
    (r'/account/([^/]+)/fans', AccountFansHandler),
    (r'/account/([^/]+)/message/fans/([^/]+)', MessageHandler),
    (r'/account/([^/]+)/auto/follow', AutoResponseHandler),
    (r'/account/([^/]+)/auto/message', AutoResponseMessageHandler),
    (r'/account/([^/]+)/menu', MenuHandler),
    (r'/account/([^/]+)/image/upload', UploadImageHandler),
    (r'/account/([^/]+)/image/list', ImageListHandler),
    (r'/account/([^/]+)/roll', ImageListHandler),
    (r'/account/([^/]+)/form', FormHandler),
    (r'/account/([^/]+)/form/new', NewFormHandler),
    (r'/account/([^/]+)/form/([^/]+)/data', FormDataHandler),
    (r'/account/([^/]+)/card', CardHandler),
]

