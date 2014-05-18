#coding:utf-8
__author__ = 'houxiaohou'

import time
import datetime
import math
from dateutil import parser
from tornado.web import HTTPError
from weishi.libs.handler import BaseHandler
from weishi.handlers.account import AccountBaseHandler
from weishi.libs.decorators import event_auth
from weishi.libs.service import AccountManager, ScratchManager, FansManager
from weishi.libs.key_util import generate_digits


class ScratchAdminHandler(AccountBaseHandler):
    """刮刮乐管理类"""

    @event_auth
    def get(self, aid):
        scratch = self.scratch_manager.get_scratch(self.account.aid)
        start = None
        end = None
        active = 0
        current = int(time.time())
        if scratch:
            start = datetime.datetime.fromtimestamp(scratch.start)
            end = datetime.datetime.fromtimestamp(scratch.end)
            active = scratch.active
        self.render('account/event_scratch.html', index='event', top='scratch', account=self.account, scratch=scratch,
                    start=start, end=end, active=active, current=current)

    @event_auth
    def post(self, *args, **kwargs):
        scratch = self.scratch_manager.get_scratch(self.account.aid)
        start = self.get_argument('start', None)
        end = self.get_argument('end', None)
        times = int(self.get_argument('times', None))
        description = self.get_argument('description', None)
        prize_1 = self.get_argument('prize_1', None)
        prize_2 = self.get_argument('prize_2', None)
        prize_3 = self.get_argument('prize_3', None)
        num_1 = int(self.get_argument('num_1', 0))
        num_2 = int(self.get_argument('num_2', 0))
        num_3 = int(self.get_argument('num_3', 0))
        s = time.mktime(parser.parse(start).timetuple())
        e = time.mktime(parser.parse(end).timetuple())
        if s >= e:
            self.write({'r': 0, 'e': u'结束日期不能小于开始日期'})
            self.finish()
            return
        if not scratch:
            self.scratch_manager.save_scratch(s, e, int((e - s) / 1000), self.account.aid, prize_1, prize_2, prize_3,
                                              num_1, num_2, num_3, num_1 + num_2 + num_3, 1, times, description)
        else:
            self.scratch_manager.update_scratch(s, e, int((e - s) / 1000), self.account.aid, prize_1, prize_2, prize_3,
                                                num_1, num_2, num_3, num_1 + num_2 + num_3, 1, times, description)
        self.write({'r': 1})
        self.finish()
        return


class ScratchHistoryHandler(AccountBaseHandler):

    @event_auth
    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 20
        total = self.scratch_manager.scratch_history_count(aid)
        total_page = math.ceil(float(total) / page_size)
        prefix = '/account/' + aid + '/event/scratch/history'
        results = self.scratch_manager.list_scratch_history(aid, int(start), page_size)
        self.render('account/event_scratch_result.html', index='event', top='scratch', account=self.account,
                    prefix=prefix, total=total, total_page=total_page, page_size=page_size, start=start,
                    results=results)


class ScratchStatusHandler(AccountBaseHandler):

    def get(self, aid):
        status = self.get_argument('status', 0)
        self.scratch_manager.change_status(aid, int(status))
        self.write({'r': 1})
        self.finish()
        return


class ScratchHandler(BaseHandler):
    """刮刮乐抽奖"""
    account_manager = None
    scratch_manager = None
    fans_manager = None

    def prepare(self):
        self.account_manager = AccountManager(self.db)
        self.scratch_manager = ScratchManager(self.db)
        self.fans_manager = FansManager(self.db)

    def get(self, aid):
        """访问抽奖页面"""
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        scratch = self.scratch_manager.get_scratch(aid)
        if not scratch:
            raise HTTPError(404)
        openid = self.get_argument('i', None)
        fans = self.fans_manager.get_fans_by_openid_aid(openid, aid)
        if not fans:
            raise HTTPError('无效的用户')
        num = self.scratch_manager.get_scratch_num_by_openid(openid, aid)
        hit_num = self.scratch_manager.get_hit_scratch_num_by_openid(openid, aid)
        # 抽奖活动持续总时间
        current = int(time.time())
        hit = 0
        hit_prize = ''
        sn = 0
        _id = 0

        if not hit_num and num < scratch.times and scratch.start < current < scratch.end and scratch.active:
            # 去抽奖
            length = scratch.length
            num_sum = scratch.num_sum
            # 抽奖间隔
            offset = int(length) / int(num_sum)
            count_start = current - offset
            since = datetime.datetime.fromtimestamp(count_start)
            since_hit_num = self.scratch_manager.hit_num_since_date(aid, since)
            if not since_hit_num:
                # 之前的没被抽中，中奖
                sn = generate_digits(8)
                num_limit = [scratch.num_1, scratch.num_2, scratch.num_3]
                for i in range(3, 0, -1):
                    if num_limit[i-1] > self.scratch_manager.hit_num_by_pirze(aid, i):
                        hit = 1
                        if i == 3:
                            hit_prize = '三等奖'
                        elif i == 2:
                            hit_prize = '二等奖'
                        elif i == 1:
                            hit_prize = '一等奖'
                        _id = int(self.scratch_manager.save_scratch_result(aid, openid, i, sn))
                        break
            else:
                self.scratch_manager.save_scratch_result(aid, openid, 0, 0)
        if not sn:
            self.scratch_manager.save_scratch_result(aid, openid, 0, 0)
        self.render('event/scratch.html', scratch=scratch, account=account, openid=openid, num=num, hit_num=hit_num,
                    hit=hit, hit_prize=hit_prize, sn=sn, id=_id)

    def post(self, *args, **kwargs):
        """中奖用户提交手机号"""
        openid = self.get_argument('openid', None)
        _id = self.get_argument('id', 0)
        sn = self.get_argument('sn', None)
        phone = self.get_argument('phone', None)
        self.scratch_manager.update_scratch_phone(openid, int(sn), int(_id), phone)
        self.write({'r': 1})

handlers = [
    (r'/event/scratch/([^/]+)', ScratchHandler),
    (r'/account/([^/]+)/event/scratch', ScratchAdminHandler),
    (r'/account/([^/]+)/event/scratch/status', ScratchStatusHandler),
    (r'/account/([^/]+)/event/scratch/results', ScratchHistoryHandler),
]