#coding:utf-8
__author__ = 'young'

import json
import urllib
from tornado.web import RequestHandler
from tornado.web import HTTPError

from weishi.libs.service import (
    FormManager,
    FansManager,
    CardManager,
    AccountManager,
    ImpactManager,
    SiteManager,
    AnalyticsManager)
from weishi.libs.handler import BaseHandler
from weishi.libs import key_util


class IndexHandler(RequestHandler):
    def get(self):
        self.render('event/shake.html')


class FormHandler(BaseHandler):
    """浏览表单"""

    form_manager = None

    def prepare(self):
        self.form_manager = FormManager(self.db)

    def get(self, fid):
        """返回表单页面"""
        form = self.form_manager.get_form_by_fid(fid)
        if not form:
            raise HTTPError(404)
        items = json.loads(form.content)
        self.render('front/form.html', form=form, items=items)

    def post(self, *args, **kwargs):
        """提交表单"""
        form = self.form_manager.get_form_by_fid(args[0])
        items = self.request.body.split('&')
        result = {}
        for item in items:
            k, v = map(urllib.unquote, item.split('='))
            result[k] = v
        self.form_manager.save_input_to_form_content(form.fid, json.dumps(result, ensure_ascii=False))
        self.render('front/form-success.html')


class CardHandler(BaseHandler):
    """会员卡服务"""

    fans_manager = None
    card_manager = None
    account_manager = None

    def prepare(self):
        self.fans_manager = FansManager(self.db)
        self.card_manager = CardManager(self.db)
        self.account_manager = AccountManager(self.db)

    def get(self, cid):
        """
        用户访问会员卡页面
        1. 如果已经有会员卡，返回信息
        2. 如果没有
            1. 如果会员卡允许自动创建，则自动创建
            2. 如果不允许自动创建，按照要求填写表单
        """
        card = self.card_manager.get_card_by_cid(cid)
        openid = self.get_argument('i', None)
        if not openid or not card:
            raise HTTPError(404)
        fans = self.fans_manager.get_fans_by_openid(openid)
        if not fans:
            pass
        account = self.account_manager.get_account_by_aid(card.aid)
        card_member = self.card_manager.get_user_card_info(cid, openid)
        rule = self.card_manager.get_account_card_rule(card.aid)
        if card_member:
            historys = self.card_manager.get_history_by_openid(card.aid, openid)
            self.render('front/card.html', member=card_member, card=card, account=account, rule=rule, historys=historys)
            return
        if card.register == 1:
            # 自动注册
            card_id = card.id
            num = key_util.generate_digits_starts_with(str(card_id), 7)
            num = str(card_id) + num
            self.card_manager.save_member(card.aid, cid, num, openid, '', '', '')
            card_member = self.card_manager.get_user_card_info(cid, openid)
            self.render('front/card.html', member=card_member, account=account, card=card)
            return
        else:
            # 返回注册卡片页面
            m = self.get_argument('m', None)
            self.render('front/card_reg.html', card=card, openid=openid, account=account, m=m)

    def post(self, *args, **kwargs):
        """提交领取会员卡的表单"""
        result = {'r': 0}
        openid = self.get_argument('openid', None)
        mobile = self.get_argument('mobile', None)
        address = self.get_argument('address', None)
        sex = self.get_argument('sex', None)
        birthday = self.get_argument('birthday', None)
        name = self.get_argument('name', '')
        if not openid:
            result['error'] = '出了点错误，重新注册吧~'
            self.write(result)
            return
        card = self.card_manager.get_card_by_cid(args[0])
        if not card:
            result['error'] = '你来到了一个不存在的页面~'
            self.write(result)
            return
        if card.mobile and not mobile:
            result['error'] = '手机号一定要填哦~'
            self.write(result)
            return
        if card.address and not address:
            result['error'] = '地址一定要填哦~'
            self.write(result)
            return
        if card.sex and not sex:
            result['error'] = '性别一定要选哦~'
            self.write(result)
            return
        if card.birthday and not birthday:
            result['error'] = '生日一定要填哦~'
            self.write(result)
            return
        card_id = card.id
        num = key_util.generate_digits_starts_with(str(card_id), 7)
        num = str(card_id) + num
        self.card_manager.save_member(card.aid, card.cid, num, openid, name, mobile, address, sex, birthday)
        result['r'] = 1
        result['openid'] = openid
        self.write(result)
        return


class ImpactHandler(BaseHandler):
    impact_manager = None

    def prepare(self):
        self.impact_manager = ImpactManager(self.db)

    def get(self, aid):
        """查看用户印象"""
        impacts = self.impact_manager.list_impact(aid)
        total = self.impact_manager.total_impact_num(aid)
        name = self.get_cookie('i_%s' % aid, None)
        if name:
            try:
                name = "".join([(len(i) > 0 and unichr(int(i, 16)) or "") for i in name.split('%u')])
            except ValueError:
                name = None
        self.render('front/impact.html', impacts=impacts, total=total, name=name, aid=aid)

    def post(self, *args, **kwargs):
        """用户添加印象"""
        result = {'r': 0}
        aid = args[0]
        has = self.get_cookie('i_%s' % aid, None)
        if has:
            result['error'] = '已经添加过印象了~'
            self.write(result)
            return
        _id = self.get_argument('id', None)
        if _id:
            self.impact_manager.vote_to_impact(int(_id))
        result['r'] = 1
        self.write(result)


class GeoHandler(BaseHandler):
    """坐标转换工具"""

    def get(self):
        self.render('front/geo.html')


class SiteHandler(BaseHandler):
    site_manager = None

    def prepare(self):
        self.site_manager = SiteManager(self.db)

    def get(self, aid):
        site = self.site_manager.get_site(aid)
        openid = self.get_argument('i', '')
        if not site:
            raise HTTPError(404)
        site_ul = self.site_manager.get_site_ul(aid)
        images = [site.img1 if site.img1 else None, site.img2 if site.img2 else None, site.img3 if site.img3 else None,
                  site.img4 if site.img4 else None, site.img5 if site.img5 else None]
        self.render('front/site.html', site=site, site_ul=site_ul, images=images, openid=openid)


class ShareHandler(BaseHandler):
    analytics_manager = None
    fans_manager = None
    card_manager = None

    def prepare(self):
        self.analytics_manager = AnalyticsManager(self.db)
        self.fans_manager = FansManager(self.db)
        self.card_manager = CardManager(self.db)

    def get(self):
        openid = self.get_argument('openid', None)
        slug = self.get_argument('slug', None)
        aid = self.get_argument('aid', None)
        msg = self.get_argument('msg', None)
        success = 1
        _type = '好友'
        print '%s - %s - %s - %s' % (openid, slug, aid, msg)
        if msg and 'cancel' in msg:
            success = 0
        if msg and 'timeline' in msg:
            _type = '朋友圈'
        self.analytics_manager.save_share_history(openid, slug, success, _type, aid)
        if openid:
            fans = self.fans_manager.get_fans_by_openid(openid)
            if not fans:
                return
            aid = fans.aid
            rule = self.card_manager.get_account_card_rule(aid)
            if not rule or not rule.share:
                return
            card = self.card_manager.get_card_by_aid(aid)
            if not card:
                return
            member = self.card_manager.get_user_card_info(card.cid, openid)
            if not member:
                return
            self.card_manager.new_history(aid, openid, '分享文章', rule.share, member.num)
        self.write('1')


handlers = [
    (r'/index/test', IndexHandler),
    (r'/form/([^/]+)', FormHandler),
    (r'/card/([^/]+)', CardHandler),
    (r'/impact/([^/]+)', ImpactHandler),
    (r'/site/([^/]+)', SiteHandler),
    (r'/geo', GeoHandler),
    (r'/share', ShareHandler),
]