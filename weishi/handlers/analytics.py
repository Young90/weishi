#coding:utf-8
__author__ = 'houxiaohou'


from weishi.handlers.account import AccountBaseHandler


class AnalyticsHandler(AccountBaseHandler):

    def get(self, aid):
        self.render('account/analytics_overview.html', account=self.account, index='analytics')


handlers = [
    (r'/account/([^/]+)/analytics', AnalyticsHandler),
]