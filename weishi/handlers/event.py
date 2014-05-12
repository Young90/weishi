#coding:utf-8
__author__ = 'houxiaohou'

import time
from dateutil import parser
from tornado.web import RequestHandler
from weishi.handlers.account import AccountBaseHandler


class ScratchAdminHandler(AccountBaseHandler):
    """刮刮乐管理类"""

    def get(self, aid):
        scratch = self.scratch_manager.get_scratch(self.account.aid)
        self.render('account/event_scratch.html', index='event', top='scratch', account=self.account, scratch=scratch)

    def post(self, *args, **kwargs):
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
        self.scratch_manager.save_scratch(s, e, int((e - s) / 1000), self.account.aid, prize_1, prize_2, prize_3,
                                          num_1, num_2, num_3, num_1 + num_2 + num_3, 1, times, description)
        self.write({'r': 1})
        self.finish()
        return


class ScratchHandler(RequestHandler):
    def get(self, aid):
        self.render('event/scratch.html')


handlers = [
    (r'/event/scratch/([^/]+)', ScratchHandler),
    (r'/account/([^/]+)/event/scratch', ScratchAdminHandler),
]