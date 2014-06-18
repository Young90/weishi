# coding:utf-8
import math

__author__ = 'houxiaohou'

from tornado.web import HTTPError
from weishi.libs.decorators import canyin_auth
from weishi.libs.handler import BaseHandler
from weishi.handlers.account import AccountBaseHandler
from weishi.libs.service import CanyinManager, AccountManager, FansManager
from torndb import Row
import simplejson


class CanyinFrontHandler(BaseHandler):
    canyin_manager = None
    account_manager = None
    fans_manager = None

    def prepare(self):
        self.canyin_manager = CanyinManager(self.db)
        self.account_manager = AccountManager(self.db)
        self.fans_manager = FansManager(self.db)


class MenuHandler(CanyinFrontHandler):
    def get(self, aid):
        i = self.get_argument('i')
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        cates = self.canyin_manager.list_cate(aid)
        cate_id = cates[0].id
        dish = self.canyin_manager.list_dish_by_cate(aid, cate_id)
        nums = {}
        for d in dish:
            h = self.canyin_manager.get_my_dish_by_dish_id(aid, i, d.id)
            if h:
                nums[d.id] = h.num
            else:
                nums[d.id] = 0
        self.render('menu/menu.html', aid=aid, cates=cates, dish=dish, nums=nums, i=i, account=account)


class DishHandler(CanyinFrontHandler):
    def post(self, *args, **kwargs):
        aid = args[0]
        i = self.get_argument('i', None)
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            self.write({'r': 0, 'e': 'invalid account'})
            return
        cate = self.get_argument('cate', 0)
        cate = int(cate)
        dish = self.canyin_manager.list_dish_by_cate(aid, int(cate))
        results = []
        for d in dish:
            h = self.canyin_manager.get_my_dish_by_dish_id(aid, i, d.id)
            if h:
                o2u_num = h.num
            else:
                o2u_num = 0
            r = {'id': int(d.id), 'name': d.name, 'img': d.img, 'unit': d.unit, 'price': d.price,
                 'cate_id': d.cate_id, 'description': d.description, 'num': d.num, 'special': d.special,
                 'special_price': d.special_price, 'hot': d.hot, 'o2u_num': o2u_num}
            results.append(r)
        result = {'r': 1, 'cate': cate, 'results': results}
        self.write(result)


class MyDishHandler(CanyinFrontHandler):
    def get(self, aid):
        i = self.get_argument('i')
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        my_list = self.canyin_manager.list_my(i, aid)
        dish = {}
        for m in my_list:
            d = self.canyin_manager.get_dish_by_id(aid, m.dish_id)
            dish[m.dish_id] = d
        self.render('menu/my.html', aid=aid, i=i, dish=dish, my_list=my_list, account=account)


class RemoveMyDishHandler(CanyinFrontHandler):
    def get(self, aid):
        i = self.get_argument('i')
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        self.canyin_manager.remove_all_my_dish(aid, i)
        self.redirect('/module/canyin/' + aid + '?i=' + i)


class MyShareHandler(CanyinFrontHandler):
    def get(self, aid):
        f = self.get_argument('f')
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        my_list = self.canyin_manager.list_my(f, aid)
        dish = {}
        total = 0
        for m in my_list:
            d = self.canyin_manager.get_dish_by_id(aid, m.dish_id)
            dish[m.dish_id] = d
            num = m.num
            total += num * float(d.special_price) if d.special else num * float(d.price)
        self.render('menu/my_share.html', aid=aid, dish=dish, my_list=my_list, total=int(total), account=account)


class AutoChooseHandler(CanyinFrontHandler):
    def get(self, aid):
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        num_list = self.canyin_manager.list_menu_num(aid)
        nums = []
        for _n in num_list:
            nums.append(int(_n['num']))
        nums.sort()
        i = self.get_argument('i')
        self.render('menu/auto_choose.html', aid=aid, nums=nums, i=i)


class ShowMenuHandler(CanyinFrontHandler):
    def get(self, aid):
        num = int(self.get_argument('num', 0))
        i = self.get_argument('i', None)
        mid = int(self.get_argument('mid', 0))
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        menu_list = self.canyin_manager.list_menu_by_num(aid, num)
        mid_list = []
        for _m in menu_list:
            mid_list.append(int(_m.id))
        if mid == 0:
            menu = menu_list[0]
        else:
            menu = self.canyin_manager.get_menu_by_id(aid, mid)
        dish_list = menu.dish_list.split(',')
        ds = []
        for _d in dish_list:
            ds.append(self.canyin_manager.get_dish_by_id(aid, int(_d)))
        index = mid_list.index(int(menu.id))
        size = len(mid_list)
        if index < size - 1:
            change_link = '/module/canyin/%s/dish/choose?num=%s&i=%s&mid=%s' % (aid, num, i, mid_list[index + 1])
        else:
            change_link = '/module/canyin/%s/dish/choose?num=%s&i=%s&mid=%s' % (aid, num, i, mid_list[0])
        self.render('menu/choose.html', aid=aid, i=i, ds=ds, menu=menu, num=num, change_link=change_link)


class AddMenuToMyHandler(CanyinFrontHandler):
    def get(self, aid):
        i = self.get_argument('i', None)
        fans = self.fans_manager.get_fans_by_openid(i)
        if not i or not fans:
            raise HTTPError(404)
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            raise HTTPError(404)
        mid = int(self.get_argument('mid', None))
        clear = int(self.get_argument('clear', 0))
        if clear:
            self.canyin_manager.remove_all_my_dish(aid, i)
        menu = self.canyin_manager.get_menu_by_id(aid, mid)
        if not menu or aid != menu.aid:
            raise HTTPError(404)
        dish_list = menu.dish_list.split(',')
        for _d in dish_list:
            dish = self.canyin_manager.get_dish_by_id(aid, int(_d))
            if dish:
                self.canyin_manager.add_to_my(aid, i, dish.id, dish.cate_id)
        self.redirect('/module/canyin/%s/dish/my?i=%s' % (aid, i))


class BookHandler(CanyinFrontHandler):
    def get(self, aid):
        stores = self.canyin_manager.list_store(aid)
        self.render('menu/book.html', stores=stores)


class CateNumHandler(CanyinFrontHandler):
    def post(self, *args, **kwargs):
        aid = args[0]
        i = self.get_argument('i', None)
        fans = self.fans_manager.get_fans_by_openid(i)
        if not i or not fans:
            self.write({'r': 0, 'e': 'invalid user'})
            return
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            self.write({'r': 0, 'e': 'invalid account'})
            return
        cates = self.canyin_manager.list_cate(aid)
        rs = {}
        for _c in cates:
            rs[_c.id] = self.canyin_manager.count_my_by_cate(aid, i, _c.id)
        result = {'data': rs}
        self.write({'result': result})


class UpdateDishHandler(CanyinFrontHandler):
    def post(self, *args, **kwargs):
        aid = args[0]
        action = self.get_argument('action', None)
        dish_id = int(self.get_argument('dish_id', 0))
        i = self.get_argument('i', None)
        fans = self.fans_manager.get_fans_by_openid(i)
        if not i or not fans:
            self.write({'r': 0, 'e': 'invalid user'})
            return
        account = self.account_manager.get_account_by_aid(aid)
        if not account:
            self.write({'r': 0, 'e': 'invalid account'})
            return
        dish = self.canyin_manager.get_dish_by_id(aid, dish_id)
        if not dish:
            self.write({'r': 0, 'e': 'invalid dish'})
            return
        if action == 'add':
            if self.canyin_manager.have_in(aid, dish_id, i):
                self.canyin_manager.increase_my_dish_num(dish_id)
            else:
                self.canyin_manager.add_to_my(aid, i, dish_id, int(dish.cate_id))
            self.canyin_manager.increase_dish_ordered_num(aid, dish_id)
        if action == 'remove':
            dish = self.canyin_manager.get_my_dish_by_dish_id(aid, i, dish_id)
            if dish and dish.num == 1:
                self.canyin_manager.remove_my_dish(dish_id, i)
            else:
                self.canyin_manager.decrease_my_dish_num(i, dish_id)
            self.canyin_manager.decrease_dish_ordered_num(aid, dish_id)
        self.write({'r': 1})


class CanyinDishHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        cs = self.canyin_manager.list_cate(aid)
        cates = {}
        for c in cs:
            cates[str(c.id)] = Row(c)
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
        image = ps['image']
        dish = self.canyin_manager.get_dish_by_id(self.account.aid, did)
        if not did or not dish:
            self.canyin_manager.save_dish(self.account.aid, name, price, unit, image, cate, special, special_price,
                                          rank, count, hot, describe)
        else:
            self.canyin_manager.update_dish(did, self.account.aid, name, price, unit, image, cate, special,
                                            special_price, rank, count, hot, describe)
        self.write({'r': 1})
        self.finish()


class CanyinHistoryDishHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 20
        total = self.canyin_manager.history_count(aid)
        total_page = math.ceil(float(total) / page_size)
        prefix = '/account/' + aid + '/canyin/dish/history?'
        dish = self.canyin_manager.history_list(aid, int(start), page_size)
        members = {}
        ds = {}
        for _d in dish:
            try:
                members[_d.openid]
            except Exception:
                members[_d.openid] = self.fans_manager.get_fans_by_openid(_d.openid)
            try:
                ds[_d.dish_id]
            except Exception:
                ds[_d.dish_id] = self.canyin_manager.get_dish_by_id(aid, _d.dish_id)
        self.render('account/canyin_history.html', top='history', index='canyin', account=self.account, start=start,
                    page_size=page_size, total=total, total_page=total_page, prefix=prefix, dish=dish, fans=members,
                    ds=ds)


class AutoDishHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        menu = self.canyin_manager.list_menu(aid)
        self.render('account/canyin_auto_list.html', account=self.account, index='canyin', top='auto', menu=menu)

    @canyin_auth
    def delete(self, *args, **kwargs):
        _id = self.get_argument('id', 0)
        print _id
        self.canyin_manager.delete_menu(self.account.aid, int(_id))
        self.write({'r': 1})
        self.finish()


class AutoNewDishHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        self.render('account/canyin_auto_new.html', account=self.account, index='canyin', top='auto')

    @canyin_auth
    def post(self, *args, **kwargs):
        num = self.get_argument('num', 0)
        name = self.get_argument('name', None)
        dish = self.get_argument('dish', None)
        dish = str(dish).replace(' ', '').replace('，', ',')
        total = 0
        for _d in dish.split(','):
            d = self.canyin_manager.get_dish_by_id(self.account.aid, int(_d))
            if d:
                total += int(d.special_price) if d.special else int(d.price)
        self.canyin_manager.save_menu(self.account.aid, name, int(num), dish, total)
        self.write({'r': 1})
        self.finish()


class BookListHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        stores = self.canyin_manager.list_store(aid)
        self.render('account/canyin_book_list.html', account=self.account, stores=stores, index='canyin', top='book')

    @canyin_auth
    def delete(self, *args, **kwargs):
        _id = self.get_argument('id', None)
        try:
            _id = int(_id)
        except Exception:
            _id = 0
        self.canyin_manager.delete_store(_id, self.account.aid)
        self.write({'r': 1})
        self.finish()
        return


class BookNewHandler(AccountBaseHandler):
    @canyin_auth
    def get(self, aid):
        _id = self.get_argument('id', 0)
        store = None
        if _id:
            store = self.canyin_manager.get_store_by_id(_id, aid)
        if not store:
            store = Row({'id': 0, 'name': '', 'phone': '', 'address': '', 'map': '', 'rank': 0, 'image': None})
        self.render('account/canyin_book_new.html', account=self.account, index='canyin', top='book', store=store)

    @canyin_auth
    def post(self, *args, **kwargs):
        sid = self.get_argument('sid', 0)
        name = self.get_argument('name', None)
        address = self.get_argument('address', None)
        phone = self.get_argument('phone', None)
        mp = self.get_argument('map', None)
        rank = self.get_argument('rank', 0)
        image = self.get_argument('image', None)
        store = self.canyin_manager.get_store_by_id(int(sid), self.account.aid)
        if store:
            self.canyin_manager.update_store(store.id, self.account.aid, name, image, address, mp, phone, int(rank))
        else:
            self.canyin_manager.save_store(self.account.aid, name, image, address, mp, phone, int(rank))
        self.write({'r': 1})
        self.finish()


handlers = [
    (r'/module/canyin/([^/]+)', MenuHandler),
    (r'/module/canyin/([^/]+)/dish', DishHandler),
    (r'/module/canyin/([^/]+)/cate_num', CateNumHandler),
    (r'/module/canyin/([^/]+)/dish/update', UpdateDishHandler),
    (r'/module/canyin/([^/]+)/dish/my', MyDishHandler),
    (r'/module/canyin/([^/]+)/dish/my/remove', RemoveMyDishHandler),
    (r'/module/canyin/([^/]+)/dish/my/share', MyShareHandler),
    (r'/module/canyin/([^/]+)/dish/auto_choose', AutoChooseHandler),
    (r'/module/canyin/([^/]+)/dish/choose', ShowMenuHandler),
    (r'/module/canyin/([^/]+)/dish/menu', AddMenuToMyHandler),
    (r'/module/canyin/([^/]+)/book', BookHandler),
    (r'/account/([^/]+)/canyin/cate', CanyinCateHandler),
    (r'/account/([^/]+)/canyin/dish', CanyinDishHandler),
    (r'/account/([^/]+)/canyin/dish/new', CanyinNewDishHandler),
    (r'/account/([^/]+)/canyin/dish/history', CanyinHistoryDishHandler),
    (r'/account/([^/]+)/canyin/dish/auto', AutoDishHandler),
    (r'/account/([^/]+)/canyin/dish/auto/new', AutoNewDishHandler),
    (r'/account/([^/]+)/canyin/book', BookListHandler),
    (r'/account/([^/]+)/canyin/book/new', BookNewHandler),
]