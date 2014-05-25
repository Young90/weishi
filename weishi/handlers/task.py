#coding:utf-8
__author__ = 'houxiaohou'

import time

from weishi.libs.handler import BaseHandler
from weishi.libs.service import AccountManager, CardManager, FansManager, AnalyticsManager


class CardPointBase(BaseHandler):

    account_manager = None
    card_manager = None
    fans_manager = None
    analytics_manager = None

    TYPE_FOLLOW = '起始积分'
    TYPE_TIME = '满30天累计积分'
    TYPE_SHARE = '分享文章'

    def prepare(self):
        self.account_manager = AccountManager(self.db)
        self.card_manager = CardManager(self.db)
        self.fans_manager = FansManager(self.db)
        self.analytics_manager = AnalyticsManager(self.db)

    def update_account_member_score(self, aid):
        rule = self.card_manager.get_account_card_rule(aid)
        if not rule:
            return
        follow = rule.follow
        times = rule.time
        share = rule.share
        card = self.card_manager.get_card_by_aid(aid)
        if not card:
            return
        members = self.card_manager.list_card_member(aid, card.cid, 0, 0, 10000)
        now = int(time.time())
        for m in members:
            try:
                f = self.fans_manager.get_fans_by_openid(m.openid)
                openid = f.openid
                subscribe_time = f.subscribe_time
                s_time = int(time.mktime(subscribe_time.timetuple()))
                month = int((now - s_time) / (60 * 60 * 24 * 30))
                time_point = times * month
                history = self.card_manager.get_history_by_type(str(f.openid), str(aid), self.TYPE_TIME)
                if not history:
                    self.card_manager.new_history(aid, f.openid, self.TYPE_TIME, time_point, m.num)
                else:
                    self.card_manager.update_history_by_type(f.openid, time_point, self.TYPE_TIME)
                if not self.card_manager.get_history_by_type(f.openid, aid, self.TYPE_FOLLOW):
                    self.card_manager.new_history(aid, f.openid, self.TYPE_FOLLOW, follow, m.num)
                else:
                    self.card_manager.update_history_by_type(f.openid, follow, self.TYPE_FOLLOW)
                share_count = self.analytics_manager.count_share_by_openid(aid, m.openid)
                print share_count
                history = self.card_manager.get_history_by_type(f.openid, aid, self.TYPE_SHARE)
                if share_count and not history:
                    self.card_manager.new_history(aid, openid, self.TYPE_SHARE, int(share_count) * share, m.num)
                if share_count and history:
                    self.card_manager.update_history_by_type(openid, int(share_count) * share, self.TYPE_SHARE)
            except Exception:
                continue


class CardPointHandler(CardPointBase):
    """用户积分更新"""

    def get(self):
        c_aid = self.get_cookie('aid', None)
        aid = self.get_argument('aid', None)
        if not c_aid or aid != c_aid:
            self.write({'r': 0})
        account = self.account_manager.get_account_by_aid(aid)
        if not aid or not account:
            self.write({'r': 0, 'e': u'invalid aid'})
            return
        self.update_account_member_score(aid)
        self.card_manager.update_all_member_point()
        self.write({'r': 1})


class CardPointAllHandler(CardPointBase):
    """
    更改所有账户会员积分
    """

    def get(self):
        accounts = self.account_manager.list_accounts(0, 1000)
        for a in accounts:
            self.update_account_member_score(a.aid)
        self.card_manager.update_all_member_point()
        self.write({'r': 1})


handlers = [
    (r'/task/card', CardPointHandler),
    (r'/task/card/all', CardPointAllHandler),
]