#coding:utf-8
__author__ = 'houxiaohou'

import time
import datetime
import math

from dateutil import parser
from tornado.web import HTTPError

from weishi.libs.handler import BaseHandler
from weishi.handlers.account import AccountBaseHandler
from weishi.libs.service import AccountManager, EventManager, FansManager, CardManager
from weishi.libs.key_util import generate_digits
from weishi.libs.decorators import authenticated, event_auth


class EventBaseHandler(BaseHandler):
    """
    用户管理微信号的base handler
    用户进入/account/{aid}/*的页面，保证获取的access_token可用
    """

    account = None
    fans_manager = None
    account_manager = None
    card_manager = None
    event_manager = None

    TYPE_SCRATCH = 'scratch'
    TYPE_LOTTERY = 'lottery'

    @authenticated
    def prepare(self):
        self.fans_manager = FansManager(self.db)
        self.account_manager = AccountManager(self.db)
        self.card_manager = CardManager(self.db)
        self.event_manager = EventManager(self.db)

        aid = self.request.uri.split('/')[2]
        if not aid:
            raise HTTPError(404)
        self.account = self.account_manager.get_account_by_aid(aid)


class EventAdminHandler(EventBaseHandler):
    """刮刮乐管理类"""

    @event_auth
    def get(self, aid, e_name):
        event = self.event_manager.get_event(self.account.aid, e_name)
        start = None
        end = None
        active = 0
        current = int(time.time())
        if event:
            start = datetime.datetime.fromtimestamp(event.start)
            end = datetime.datetime.fromtimestamp(event.end)
            active = event.active
        if e_name == self.TYPE_SCRATCH:
            self.render('account/event_scratch.html', index='event', top='scratch', account=self.account, scratch=event,
                        start=start, end=end, active=active, current=current)
            return
        if e_name == self.TYPE_LOTTERY:
            self.render('account/event_lottery.html', index='event', top='lottery', account=self.account, scratch=event,
                        start=start, end=end, active=active, current=current)
            return

    @event_auth
    def post(self, *args, **kwargs):
        e_name = args[1]
        event = self.event_manager.get_event(self.account.aid, e_name)
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
        if not event:
            self.event_manager.save_event(s, e, int((e - s) / 1000), self.account.aid, prize_1, prize_2, prize_3,
                                          num_1, num_2, num_3, num_1 + num_2 + num_3, 1, times, description, e_name)
        else:
            self.event_manager.update_event(s, e, int((e - s) / 1000), self.account.aid, prize_1, prize_2, prize_3,
                                            num_1, num_2, num_3, num_1 + num_2 + num_3, 1, times, description, e_name)
        self.write({'r': 1})
        self.finish()
        return


class EventHistoryHandler(EventBaseHandler):
    @event_auth
    def get(self, aid, e_name):
        start = self.get_argument('start', 0)
        page_size = 20
        total = self.event_manager.event_history_count(aid, e_name)
        total_page = math.ceil(float(total) / page_size)
        prefix = '/account/' + aid + '/event/scratch/history'
        results = self.event_manager.list_event_history(aid, int(start), page_size, e_name)
        if e_name == self.TYPE_SCRATCH:
            self.render('account/event_scratch_result.html', index='event', top='scratch', account=self.account,
                        prefix=prefix, total=total, total_page=total_page, page_size=page_size, start=start,
                        results=results)
            return
        if e_name == self.TYPE_LOTTERY:
            self.render('account/event_lottery_result.html', index='event', top='lottery', account=self.account,
                        prefix=prefix, total=total, total_page=total_page, page_size=page_size, start=start,
                        results=results)


class EventStatusHandler(AccountBaseHandler):
    def get(self, aid, e_name):
        status = self.get_argument('status', 0)
        self.event_manager.change_status(aid, int(status), e_name)
        self.write({'r': 1})
        self.finish()
        return


class ScratchHandler(EventBaseHandler):
    """刮刮乐抽奖"""

    def get(self, aid):
        """访问抽奖页面"""
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        scratch = self.event_manager.get_event(aid, self.TYPE_SCRATCH)
        if not scratch:
            raise HTTPError(404)
        openid = self.get_argument('i', None)
        fans = self.fans_manager.get_fans_by_openid_aid(openid, aid)
        if not fans:
            raise HTTPError('无效的用户')
        num = self.event_manager.get_event_num_by_openid(openid, aid, self.TYPE_SCRATCH)
        hit_num = self.event_manager.get_hit_event_num_by_openid(openid, aid, self.TYPE_SCRATCH)
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
            since_hit_num = self.event_manager.hit_num_since_date(aid, since, self.TYPE_SCRATCH)
            if not since_hit_num:
                # 之前的没被抽中，中奖
                sn = generate_digits(8)
                num_limit = [scratch.num_1, scratch.num_2, scratch.num_3]
                for i in range(3, 0, -1):
                    if num_limit[i - 1] > self.event_manager.hit_num_by_pirze(aid, i, self.TYPE_SCRATCH):
                        hit = 1
                        if i == 3:
                            hit_prize = '三等奖'
                        elif i == 2:
                            hit_prize = '二等奖'
                        elif i == 1:
                            hit_prize = '一等奖'
                        _id = int(self.event_manager.save_event_result(aid, openid, i, sn, self.TYPE_SCRATCH))
                        break
            else:
                self.event_manager.save_event_result(aid, openid, 0, 0, self.TYPE_SCRATCH)
        if not sn:
            self.event_manager.save_event_result(aid, openid, 0, 0, self.TYPE_SCRATCH)
        self.render('event/scratch.html', scratch=scratch, account=account, openid=openid, num=num, hit_num=hit_num,
                    hit=hit, hit_prize=hit_prize, sn=sn, id=_id)

    def post(self, *args, **kwargs):
        """中奖用户提交手机号"""
        e_name = args[1]
        openid = self.get_argument('openid', None)
        _id = self.get_argument('id', 0)
        sn = self.get_argument('sn', None)
        phone = self.get_argument('phone', None)
        self.event_manager.update_event_phone(openid, int(sn), int(_id), phone, e_name)
        self.write({'r': 1})


class EventFrontBase(BaseHandler):

    fans_manager = None
    account_manager = None
    card_manager = None
    event_manager = None

    TYPE_SCRATCH = 'scratch'
    TYPE_LOTTERY = 'lottery'

    def prepare(self):
        self.fans_manager = FansManager(self.db)
        self.account_manager = AccountManager(self.db)
        self.card_manager = CardManager(self.db)
        self.event_manager = EventManager(self.db)


class LotteryHandler(EventFrontBase):
    """大转盘摇奖"""

    def get(self, aid):
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        scratch = self.event_manager.get_event(aid, self.TYPE_LOTTERY)
        if not scratch:
            raise HTTPError(404)
        openid = self.get_argument('i', None)
        fans = self.fans_manager.get_fans_by_openid_aid(openid, aid)
        num = self.event_manager.get_event_num_by_openid(openid, aid, self.TYPE_LOTTERY)
        if not fans:
            raise HTTPError('无效的用户')
        self.render('event/lottery.html', scratch=scratch, account=account, openid=openid, num=num)

    def post(self, *args, **kwargs):
        aid = args[0]
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            self.write({'r': 0, 'e': 'invalid account'})
            return
        openid = self.get_argument('openid', None)
        fans = self.fans_manager.get_fans_by_openid_aid(openid, args[0])
        if not fans:
            self.write({'r': 0, 'e': 'invalid user'})
            return
        event = self.event_manager.get_event(aid, self.TYPE_LOTTERY)
        if not event:
            raise HTTPError(404)
        hit_num = self.event_manager.get_hit_event_num_by_openid(openid, aid, self.TYPE_LOTTERY)
        # 抽奖活动持续总时间
        current = int(time.time())
        hit = 0
        hit_class = 0
        hit_prize = ''
        sn = 0
        _id = 0
        num = self.event_manager.get_event_num_by_openid(openid, aid, self.TYPE_LOTTERY)
        if not hit_num and num < event.times and event.start < current < event.end and event.active:
            # 去抽奖
            length = event.length
            num_sum = event.num_sum
            # 抽奖间隔
            offset = int(length) / int(num_sum)
            count_start = current - offset
            since = datetime.datetime.fromtimestamp(count_start)
            since_hit_num = self.event_manager.hit_num_since_date(aid, since, self.TYPE_LOTTERY)
            if not since_hit_num:
                # 之前的没被抽中，中奖
                sn = generate_digits(8)
                num_limit = [event.num_1, event.num_2, event.num_3]
                for i in range(3, 0, -1):
                    if num_limit[i - 1] > self.event_manager.hit_num_by_pirze(aid, i, self.TYPE_LOTTERY):
                        hit = 1
                        if i == 3:
                            hit_prize = '三等奖'
                            hit_class = 3
                        elif i == 2:
                            hit_prize = '二等奖'
                            hit_class = 2
                        elif i == 1:
                            hit_prize = '一等奖'
                            hit_class = 1
                        _id = int(self.event_manager.save_event_result(aid, openid, i, sn, self.TYPE_LOTTERY))
                        break
            else:
                self.event_manager.save_event_result(aid, openid, 0, 0, self.TYPE_LOTTERY)
        if not sn:
            self.event_manager.save_event_result(aid, openid, 0, 0, self.TYPE_LOTTERY)
        result = {'r': 1, 'hit': hit, 'id': _id, 'sn': sn, 'hit_prize': hit_prize, 'hit_num': hit_class}
        self.write(result)


class EventHitPhoneHandler(EventFrontBase):

    def post(self, *args, **kwargs):
        """中奖用户提交手机号"""
        e_name = args[1]
        openid = self.get_argument('openid', None)
        _id = self.get_argument('id', 0)
        sn = self.get_argument('sn', None)
        phone = self.get_argument('phone', None)
        print e_name
        self.event_manager.update_event_phone(openid, int(sn), int(_id), phone, e_name)
        self.write({'r': 1})


handlers = [
    (r'/event/scratch/([^/]+)', ScratchHandler),
    (r'/event/lottery/([^/]+)', LotteryHandler),
    (r'/event/([^/]+)/([^/]+)/hit', EventHitPhoneHandler),
    (r'/account/([^/]+)/event/([^/]+)', EventAdminHandler),
    (r'/account/([^/]+)/event/([^/]+)/status', EventStatusHandler),
    (r'/account/([^/]+)/event/([^/]+)/results', EventHistoryHandler),
]