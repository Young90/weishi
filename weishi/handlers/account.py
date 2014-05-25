#coding:utf-8
__author__ = 'young'

import math
import json
import StringIO

import xlwt
import simplejson
from tornado.web import HTTPError, asynchronous

from weishi.libs.decorators import authenticated, menu_auth, card_auth, site_auth, impact_auth, form_auth
from weishi.libs.handler import BaseHandler
from weishi.libs.image import list_all, upload
from weishi.libs import wei_api
from weishi.libs import key_util
from weishi.libs.service import FansManager, MessageManager, ArticleManager, AccountManager, \
    MenuManager, ImageArticleManager, AutoManager, FormManager, CardManager, ImpactManager, AutoKeywordManager, \
    SiteManager, EventManager, TemplateManager


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
    impact_manager = None
    auto_keyword_manager = None
    site_manager = None
    event_manager = None
    template_manager = None

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
        self.impact_manager = ImpactManager(self.db)
        self.auto_keyword_manager = AutoKeywordManager(self.db)
        self.site_manager = SiteManager(self.db)
        self.event_manager = EventManager(self.db)
        self.template_manager = TemplateManager(self.db)

        aid = self.request.uri.split('/')[2]
        if not aid:
            raise HTTPError(404)
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        if account.user_id != self.current_user.id:
            raise HTTPError(403)
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
        group_id = self.get_argument('group_id', 0)
        groups = self.fans_manager.get_fans_group(aid)
        page_size = 10
        fans = self.fans_manager.get_fans(aid, group_id, start, page_size)
        total = self.fans_manager.get_fans_count(aid, group_id)
        total_page = math.ceil(float(total) / page_size)
        if group_id:
            prefix = '/account/%s/fans?group_id=%s&' % (aid, group_id)
        else:
            prefix = '/account/%s/fans?' % aid
        self.render('account/fans.html', fans=fans, account=self.account, total=total,
                    start=int(start), total_page=total_page, page_size=page_size, prefix=prefix,
                    index='fans', groups=groups, group_id=group_id)

    def post(self, *args, **kwargs):
        """修改粉丝分组"""
        aid = self.get_cookie('aid')
        fans_id = self.get_argument('fans_id', 0)
        group_id = self.get_argument('group_id', 0)
        group = self.fans_manager.get_fans_group_by_id(aid, group_id)
        fans = self.fans_manager.get_fans_by_id(fans_id)
        if not fans or not group:
            result = {'r': 0, 'e': u'参数不正确'}
            self.write(result)
            self.finish()
            return
        self.fans_manager.change_fans_group(fans_id, group)
        result = {'r': 1}
        self.write(result)
        self.finish()
        return


class FansGroupHandler(AccountBaseHandler):
    def delete(self, aid):
        """移除粉丝分组"""
        group_id = self.get_argument('group_id', 0)
        group = self.fans_manager.get_fans_group_by_id(aid, group_id)
        if not group:
            self.write({'r': 0, 'e': u'分组不存在'})
            self.finish()
            return
        self.fans_manager.remove_fans_group(aid, group_id)
        self.write({'r': 1})
        self.finish()
        return

    def post(self, *args, **kwargs):
        """新建粉丝分组"""
        aid = self.get_cookie('aid')
        name = self.get_argument('name', None)
        group = self.fans_manager.get_fans_group_by_name(aid, name)
        if not name or group:
            result = {'r': 0, 'e': u'名称错误或已经存在'}
            self.write(result)
            self.finish()
            return
        self.fans_manager.new_fans_group(aid, name)
        group = self.fans_manager.get_fans_group_by_name(aid, name)
        result = {'r': 1, 'name': group.name, 'id': int(group.id), 'aid': aid}
        self.write(result)
        self.finish()
        return


class MessageHandler(AccountBaseHandler):
    """
    与某个用户之间的消息列表.发送消息
    """

    def get(self, aid):
        """与某个用户之间的消息列表"""
        fans_id = self.get_argument('openid', None)
        start = int(self.get_argument('start', 0))
        page_size = 10
        if fans_id:
            fans = self.fans_manager.get_fans_by_id(fans_id)
            print fans
            if not fans or fans.aid != self.account.aid:
                raise HTTPError(404)
            messages = self.message_manager.get_message_by_openid_aid(aid, fans.openid, start, page_size)
            for m in messages:
                m.fans = fans
            total = self.message_manager.get_message_count_by_aid_openid(aid, fans.openid)
        else:
            fans = None
            messages = self.message_manager.get_message_by_aid(aid, start, page_size)
            for m in messages:
                openid = m.openid
                fan = self.fans_manager.get_fans_by_openid(openid)
                m.fans = fan
            total = self.message_manager.get_message_count_by_aid(aid)
        total_page = math.ceil(float(total) / page_size)
        if fans:
            prefix = '/account/%s/message?openid=%s&' % (aid, fans_id)
            self.render('account/messages_fans.html', fans=fans, messages=messages, account=self.account, total=total,
                        start=start, total_page=total_page, page_size=page_size, index='message', prefix=prefix)
            return
        else:
            prefix = '/account/%s/message?' % aid
            self.render('account/messages.html', messages=messages, account=self.account, total=total,
                        start=start, total_page=total_page, page_size=page_size, index='message', prefix=prefix)
            return

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
        if result['r']:
            self.message_manager.save_message(content, openid, self.account.aid)
        self.write(result)
        self.finish()


class MenuHandler(AccountBaseHandler):
    """自定义菜单"""

    @menu_auth
    def get(self, aid):
        """设置自定义菜单的页面"""
        menu = []
        main_menu = self.menu_manager.get_main_menu_list(aid)
        if not main_menu:
            self.render('account/menu.html', menu=None, account=self.account, index='menu')
            return
        for item in main_menu:
            if item.type:
                # 如果一级菜单没有子菜单
                if item.auto_id:
                    # 自动回复
                    auto = self.auto_manager.get_auto_by_id(item.auto_id)
                    print auto
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

    @menu_auth
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
                    sub_buttons.append(sub_menu)
                menu['sub_button'] = sub_buttons
            elif _type == 'text':
                value = param['value']
                mkey = key_util.generate_hexdigits_lower(8)
                auto_id = self.auto_manager.save_text_auto_response(aid=aid, content=value, mkey=mkey, re_type='text')
                self.menu_manager.save_main_menu_item_response(aid=aid, name=name, t='click', url=None, auto_id=auto_id,
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
        """获取列表"""
        auto_list = self.auto_keyword_manager.list_auto(self.account.aid)
        print auto_list
        self.render('account/auto_response_message.html', account=self.account, index='auto', auto_list=auto_list)

    def post(self, *args, **kwargs):
        """创建关键词自动回复"""
        result = {'r': 0}
        params = self.get_argument('params', None)
        params = simplejson.loads(params, encoding='utf-8')
        if not params:
            result['error'] = '参数不正确'
            self.write(result)
            self.finish()
            return
        self.auto_keyword_manager.truncate_auto(self.account.aid)
        for param in params:
            _word = param['word']
            _type = param['type']
            _value = param['value']
            _wild = param['wild']
            if _type == 'text':
                self.auto_keyword_manager.save_content_auto_keyword(_word, _value, self.account.aid, _wild)
            elif _type == 'single':
                self.auto_keyword_manager.save_image_art_auto_keyword(_word, int(_value), self.account.aid, _wild)
            elif _type == 'multi':
                self.auto_keyword_manager.save_image_art_group_auto_keyword(_word, int(_value), self.account.aid, _wild)
        result['r'] = 1
        self.write(result)
        self.finish()


class UploadImageHandler(AccountBaseHandler):
    """上传图片接口，返回图片的url"""

    def post(self, *args, **kwargs):
        result = {'r': 0}
        try:
            file_body = self.request.files['file'][0]['body']
            url = upload(file_body, self.account.aid)
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
        urls = list_all(self.account.aid)
        results = {'r': 1, 'count': len(urls), 'urls': urls}
        self.write(results)
        self.finish()


class FormHandler(AccountBaseHandler):
    """自定义表单管理"""

    @form_auth
    def get(self, aid):
        forms = self.form_manager.get_form_list_by_aid(self.account.aid)
        self.render('account/forms.html', account=self.account, index='form', forms=forms)


class FormDataHandler(AccountBaseHandler):
    """查看表单上数据"""

    @form_auth
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

    @card_auth
    def get(self, aid):
        """
        如果还没有创建会员卡，则返回创建页面
        如果已经创建，列出会员信息
        """
        card = self.card_manager.get_card_by_aid(self.account.aid)
        if not card:
            self.render('account/card.html', account=self.account, index='card', card=None)
            return
        self.render('account/card.html', account=self.account, index='card', card=card, top='card')
        return

    @card_auth
    def post(self, *args, **kwargs):
        """提交会员卡创建信息"""
        card = self.card_manager.get_card_by_aid(self.account.aid)
        register = self.get_argument('register', 0)
        name = self.get_argument('name', 0)
        mobile = self.get_argument('mobile', 0)
        address = self.get_argument('address', 0)
        phone = self.get_argument('phone', None)
        about = self.get_argument('about', None)
        thumb = self.get_argument('thumb', None)
        cover = self.get_argument('cover', None)
        if not card:
            # 如果还没创建，则创建
            cid = key_util.generate_hexdigits_lower(8)
            self.card_manager.save_card(self.account.aid, cid, register, name, mobile, address, phone, about, cover)
            card = self.card_manager.get_card_by_aid(self.account.aid)
            self.image_article_manager.save_single_image_article('会员卡', '点击查看会员卡',
                                                                 'http://www.wsmt.cn/card/' + card.cid, thumb,
                                                                 self.account.aid)
        else:
            # 如果已经存在，则更新信息
            self.card_manager.update_card(card.cid, register, name, mobile, address, phone, about, cover)
        result = {'r': 1}
        self.write(result)
        self.finish()


class CardMemberHandler(AccountBaseHandler):
    """会员管理"""

    @card_auth
    def get(self, aid):
        """
        如果还没有创建会员卡，则跳转到创建页面
        如果已经创建，列出会员信息
        """
        card = self.card_manager.get_card_by_aid(self.account.aid)
        if not card:
            self.redirect('/account/' + aid + '/card')
            return
        start = int(self.get_argument('start', 0))
        group_id = self.get_argument('group_id', 0)
        page_size = 20
        total = self.card_manager.get_card_member_count(self.account.aid, card.cid, group_id)
        total_page = math.ceil(float(total) / page_size)
        card_members = self.card_manager.list_card_member(aid, card.cid, group_id, int(start), int(start) + page_size)
        groups = self.card_manager.list_member_groups(aid)
        prefix = '/account/%s/card/member?' % aid
        self.render('account/card_member.html', account=self.account, index='card', members=card_members, total=total,
                    total_page=total_page, page_size=page_size, start=start, card=card, groups=groups, top='member',
                    group_id=group_id, prefix=prefix)
        return

    @card_auth
    def post(self, *args, **kwargs):
        aid = self.get_cookie('aid')
        op = self.get_argument('op', None)
        member_id = int(self.get_argument('fans_id', 0))
        fans = self.card_manager.get_card_member_by_id(aid, member_id)
        if not fans:
            result = {'r': 0, 'e': u'参数不正确'}
            self.write(result)
            self.finish()
            return
        if op == 'group':
            group_id = int(self.get_argument('group_id', 0))
            group = self.card_manager.get_member_group_by_id(aid, group_id)
            if not group:
                result = {'r': 0, 'e': u'参数不正确'}
                self.write(result)
                self.finish()
                return
            self.card_manager.change_member_group(member_id, group)
            result = {'r': 1}
            self.write(result)
            self.finish()
            return
        elif op == 'point':
            try:
                point = int(self.get_argument('point', 0))
            except ValueError:
                result = {'r': 0, 'e': u'参数不正确'}
                self.write(result)
                self.finish()
                return
            self.card_manager.new_history(aid, fans.openid, '管理员修改', point, fans.num)
            self.card_manager.update_member_point_by_openid(fans.openid)
            result = {'r': 1}
            self.write(result)
            self.finish()
            return


class CardRuleHandler(AccountBaseHandler):
    @card_auth
    def get(self, aid):
        rule = self.card_manager.get_account_card_rule(aid)
        self.render('account/card_rule.html', account=self.account, rule=rule, index='card', top='point')
        return

    @card_auth
    def post(self, *args, **kwargs):
        follow = self.get_argument('follow', 0)
        times = self.get_argument('times', 0)
        share = self.get_argument('share', 0)
        message = self.get_argument('message', 0)
        rule = self.card_manager.get_account_card_rule(self.account.aid)
        if not rule:
            self.card_manager.save_card_rule(self.account.aid, follow, times, message, share)
        else:
            self.card_manager.update_card_rule(self.account.aid, follow, times, message, share)
        self.write({'r': 1})
        self.finish()
        return


class CardHistoryHandler(AccountBaseHandler):
    """积分历史"""

    @card_auth
    def get(self, aid):
        try:
            start = int(self.get_argument('start', 0))
        except ValueError:
            start = 0
        page_size = 20
        total = self.card_manager.history_count(self.account.aid)
        total_page = math.ceil(float(total) / page_size)
        history_list = self.card_manager.list_history(aid, start, page_size)
        prefix = '/account/%s/card/history?' % aid
        self.render('account/card_history.html', account=self.account, index='card', top='point', total=total,
                    start=start, total_page=total_page, history_list=history_list, page_size=page_size, prefix=prefix)


class CardExportHandler(AccountBaseHandler):
    """导出用户记录到excel"""

    @card_auth
    def get(self, aid):
        group_id = int(self.get_argument('group_id', 0))
        name = '会员信息.xls'
        if group_id:
            group = self.card_manager.get_member_group_by_id(aid, group_id)
            if not group:
                self.write({'r': 0, 'e': 'not exists'})
                self.finish()
                return
            name = group.name + '.xls'
        card = self.card_manager.get_card_by_aid(aid)
        members = self.card_manager.list_card_member(aid, card.cid, group_id, 0, 100000)
        m_file = xlwt.Workbook()
        table = m_file.add_sheet(u'全部会员')
        table.write(0, 0, 'id')
        table.write(0, 1, u'注册日期')
        table.write(0, 2, 'openid')
        table.write(0, 3, u'姓名')
        table.write(0, 4, u'会员卡号')
        table.write(0, 5, u'电话')
        table.write(0, 6, u'地址')
        table.write(0, 7, u'积分')
        table.write(0, 8, u'分组')
        for i, m in enumerate(members):
            table.write(i + 1, 0, m.id)
            table.write(i + 1, 1, m.date.strftime("%Y-%m-%d %H:%M:%S"))
            table.write(i + 1, 2, m.openid)
            table.write(i + 1, 3, m.name)
            table.write(i + 1, 4, m.num)
            table.write(i + 1, 5, m.mobile)
            table.write(i + 1, 6, m.address)
            table.write(i + 1, 7, m.point)
            table.write(i + 1, 8, m.group_name)
        f = StringIO.StringIO()
        m_file.save(f)
        self.set_header('Content-Type',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset="utf-8"')
        self.set_header('Content-Disposition', 'attachment;filename="%s";charset="utf-8";' % name)
        self.write(f.getvalue())
        self.finish()
        return


class CardMemberGroupHandler(AccountBaseHandler):
    @card_auth
    def delete(self, aid):
        """移除会员分组"""
        group_id = self.get_argument('group_id', 0)
        group = self.card_manager.get_member_group_by_id(aid, group_id)
        if not group:
            self.write({'r': 0, 'e': u'分组不存在'})
            self.finish()
            return
        self.card_manager.remove_card_member_group(group_id)
        self.write({'r': 1})
        self.finish()
        return

    @card_auth
    def post(self, *args, **kwargs):
        """新建会员分组"""
        aid = self.get_cookie('aid')
        name = self.get_argument('name', None)
        group = self.card_manager.get_member_group_by_name(aid, name)
        if not name or group:
            result = {'r': 0, 'e': u'名称错误或已经存在'}
            self.write(result)
            self.finish()
            return
        self.card_manager.new_card_member_group(aid, name)
        group = self.card_manager.get_member_group_by_name(aid, name)
        result = {'r': 1, 'name': group.name, 'id': int(group.id), 'aid': aid}
        self.write(result)
        self.finish()
        return


class ImpactHandler(AccountBaseHandler):
    """公众账号管理印象"""

    @impact_auth
    def get(self, aid):
        impacts = self.impact_manager.list_impact(self.account.aid)
        self.render('account/impact.html', account=self.account, impacts=impacts, index='impact')

    @impact_auth
    def post(self, *args, **kwargs):
        """保存用户印象"""
        result = {'r': 0}
        params = self.get_argument('params', None)
        print params
        if not params:
            result['error'] = '参数不正确'
            self.write(result)
            self.finish()
        params = simplejson.loads(params, encoding='utf-8')
        result['r'] = 1
        self.impact_manager.truncate_impacts(self.account.aid)
        for param in params:
            name = param['name']
            num = param['num']
            if name and name != '':
                self.impact_manager.save_impact(self.account.aid, name, int(num))
        self.write(result)
        self.finish()


class SiteHandler(AccountBaseHandler):
    """微官网"""

    @site_auth
    def get(self, aid):
        site = self.site_manager.get_site(aid)
        site_ul = self.site_manager.get_site_ul(aid)
        images = None
        if site:
            images = [site.img1 if site.img1 else None, site.img2 if site.img2 else None,
                      site.img3 if site.img3 else None,
                      site.img4 if site.img4 else None, site.img5 if site.img5 else None]
        self.render('account/site.html', account=self.account, site=site, site_ul=site_ul, images=images, index='site',
                    top='site')

    @site_auth
    def post(self, *args, **kwargs):
        params = self.get_argument('params', None)
        if not params:
            result = {'r': 0, 'e': u'参数不正确'}
            self.write(result)
            self.finish()
        ps = simplejson.loads(params, encoding='utf-8')
        title = ps['title']
        phone = ps['phone']
        thumb = ps['thumb']
        images = ps['images']
        img1 = None
        img2 = None
        img3 = None
        img4 = None
        img5 = None
        if images:
            img1 = images[0] if len(images) > 0 else None
            img2 = images[1] if len(images) > 1 else None
            img3 = images[2] if len(images) > 2 else None
            img4 = images[3] if len(images) > 3 else None
            img5 = images[4] if len(images) > 4 else None
        self.site_manager.initial(self.account.aid)
        self.site_manager.save_site(aid=self.account.aid, title=title, phone=phone, img1=img1, img2=img2, img3=img3,
                                    img4=img4, img5=img5)
        if thumb and len(thumb) > 0:
            self.image_article_manager.save_single_image_article('微官网', '点击查看微官网',
                                                                 'http://www.wsmt.cn/site/' + self.account.aid,
                                                                 thumb, self.account.aid)
        links = ps['links']
        if links:
            for link in links:
                self.site_manager.save_site_ul(aid=self.account.aid, name=link['name'], icon=link['icon'],
                                               link=link['link'])
        result = {'r': 1}
        self.write(result)
        self.finish()


class SiteTemplateHandler(AccountBaseHandler):
    def get(self, aid):
        self.render('account/site_template.html', account=self.account, top='sub', index='site')

    def post(self, *args, **kwargs):
        aid = self.account.aid
        params = self.get_argument('params', None)
        if not params:
            result = {'r': 0, 'e': u'参数不正确'}
            self.write(result)
            self.finish()
            return
        ps = simplejson.loads(params, encoding='utf-8')
        _type = int(ps['type'])
        title = ps['title'] if 'title' in ps else ''
        thumb = ps['thumb'] if 'thumb' in ps else ''
        lists = ps['lists'] if 'lists' in ps else ''
        slug = key_util.generate_hexdigits_lower(8)
        self.template_manager.save_template(aid, title, slug, _type, thumb)
        for i, l in enumerate(lists):
            l_title = l['title'] if 'title' in l else ''
            l_link = l['link'] if 'link' in l else ''
            l_thumb = l['thumb'] if 'thumb' in l else ''
            self.template_manager.save_template_list(slug, l_title, l_link, l_thumb, i)
        self.write({'r': 1})
        self.finish()
        return


class SiteTemplateListHandler(AccountBaseHandler):

    def get(self, aid):
        templates = self.template_manager.list_template(aid)
        self.render('account/site_template_list.html', account=self.account, top='sub', index='site',
                    templates=templates)


handlers = [
    (r'/account/([^/]+)', AccountIndexHandler),
    (r'/account/([^/]+)/fans', AccountFansHandler),
    (r'/account/([^/]+)/fans/group', FansGroupHandler),
    (r'/account/([^/]+)/message', MessageHandler),
    (r'/account/([^/]+)/auto/follow', AutoResponseHandler),
    (r'/account/([^/]+)/auto/message', AutoResponseMessageHandler),
    (r'/account/([^/]+)/menu', MenuHandler),
    (r'/account/([^/]+)/image/upload', UploadImageHandler),
    (r'/account/([^/]+)/image/list', ImageListHandler),
    (r'/account/([^/]+)/form', FormHandler),
    (r'/account/([^/]+)/form/new', NewFormHandler),
    (r'/account/([^/]+)/form/([^/]+)/data', FormDataHandler),
    (r'/account/([^/]+)/card', CardHandler),
    (r'/account/([^/]+)/card/member', CardMemberHandler),
    (r'/account/([^/]+)/card/rule', CardRuleHandler),
    (r'/account/([^/]+)/card/history', CardHistoryHandler),
    (r'/account/([^/]+)/card/export', CardExportHandler),
    (r'/account/([^/]+)/card/member/group', CardMemberGroupHandler),
    (r'/account/([^/]+)/impact', ImpactHandler),
    (r'/account/([^/]+)/site', SiteHandler),
    (r'/account/([^/]+)/site/sub', SiteTemplateHandler),
    (r'/account/([^/]+)/site/sub/list', SiteTemplateListHandler),
]