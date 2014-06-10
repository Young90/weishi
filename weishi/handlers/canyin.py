# coding:utf-8
__author__ = 'houxiaohou'

from weishi.libs.decorators import canyin_auth
from weishi.libs.handler import BaseHandler
from weishi.handlers.account import AccountBaseHandler
from weishi.libs.service import CanyinManager
from torndb import Row
import simplejson


class MenuHandler(BaseHandler):
    canyin_manager = None

    def prepare(self):
        self.canyin_manager = CanyinManager(self.db)

    def get(self, aid):
        self.render('menu/menu.html')


class CanyinDishHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        cates = self.canyin_manager.list_cate(aid)
        cate_id = self.get_argument('cate_id', 0)
        if cate_id:
            dish = self.canyin_manager.list_dish_by_cate(aid, cate_id)
        else:
            dish = self.canyin_manager.list_all_dish(aid)
        self.render('account/canyin_dish.html', account=self.account, dish=dish,
                    index='canyin', top='dish', cates=cates, cate_id=cate_id)

    def delete(self, *args, **kwargs):
        _id = self.get_argument('id', 0)
        self.canyin_manager.delete_dish(self.account.aid, _id)
        self.write({'r': 1})
        self.finish()


class CanyinCateHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        cates = self.canyin_manager.list_cate(aid)
        self.render('account/canyin_cate.html', account=self.account, dish=self.canyin_manager.list_all_dish(aid),
                    index='canyin', top='dish_cate', cates=cates)

    @canyin_auth
    def post(self, *args, **kwargs):
        name = self.get_argument('name', None)
        rank = self.get_argument('rank', None)
        _id = self.get_argument('id', 0)
        try:
            rank = int(rank)
            _id = int(_id)
        except Exception:
            rank = 0
            _id = 0
        self.canyin_manager.save_cate(self.account.aid, name, rank, _id)
        self.write({'r': 1})
        self.finish()
        return

    @canyin_auth
    def delete(self, *args, **kwargs):
        _id = self.get_argument('id', None)
        try:
            _id = int(_id)
        except Exception:
            _id = 0
        self.canyin_manager.delete_cate(self.account.aid, _id)
        self.write({'r': 1})
        self.finish()
        return


class CanyinNewDishHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        _id = self.get_argument('id', 0)
        dish = None
        if _id:
            dish = self.canyin_manager.get_dish_by_id(aid, _id)
        if not dish:
            dish = Row({'id': 0, 'name': '', 'price': '', 'cate_id': 0, 'unit': '份', 'description': '', 'num': '0',
                        'rank': 0, 'hot': 0, 'special': 0, 'special_price': '', 'vip': 0, 'vip_price': '',
                        'img': None})
        cates = self.canyin_manager.list_cate(aid)
        self.render('account/canyin_new.html', account=self.account, index='canyin', top='dish_new',
                    cates=cates, dish=dish)

    @canyin_auth
    def post(self, *args, **kwargs):
        ps = self.get_argument('params', None)
        if not ps:
            self.write({'r': 0, 'e': '参数有误'})
            self.finish()
            return
        ps = simplejson.loads(ps, encoding='utf-8')
        did = ps['did']
        name = ps['name']
        price = ps['price']
        cate = int(ps['cate'])
        unit = ps['unit']
        describe = ps['describe']
        count = int(ps['count'])
        rank = int(ps['rank'])
        hot = int(ps['hot'])
        special = int(ps['special'])
        special_price = ps['special_price']
        vip = int(ps['vip'])
        vip_price = ps['vip_price']
        image = ps['image']
        dish = self.canyin_manager.get_dish_by_id(self.account.aid, did)
        if not did or not dish:
            self.canyin_manager.save_dish(self.account.aid, name, price, unit, image, cate, special, special_price,
                                          vip, vip_price, rank, count, hot, describe)
        else:
            self.canyin_manager.update_dish(did, self.account.aid, name, price, unit, image, cate, special,
                                            special_price, vip, vip_price, rank, count, hot, describe)
        self.write({'r': 1})
        self.finish()


handlers = [
    (r'/module/canyin/([^/]+)', MenuHandler),
    (r'/account/([^/]+)/canyin/cate', CanyinCateHandler),
    (r'/account/([^/]+)/canyin/dish', CanyinDishHandler),
    (r'/account/([^/]+)/canyin/dish/new', CanyinNewDishHandler),
]