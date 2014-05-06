#coding:utf-8
__author__ = 'young'

import math
import simplejson

from tornado.web import HTTPError

from weishi.libs import key_util
from weishi.handlers.account import AccountBaseHandler
from weishi.libs.handler import BaseHandler
from weishi.libs.service import ImageArticleManager


class ImageArticleHandler(AccountBaseHandler):
    """单条图文管理"""

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        total = self.image_article_manager.get_image_article_count_by_aid(self.account.aid)
        total_page = math.ceil(float(total) / page_size)
        articles = self.image_article_manager.list_single_image_article(aid, start, page_size)
        print 'total : %s' % total
        print 'total_page : %s' % total_page
        self.render('account/material_image_article_single.html', account=self.account, total=total, start=int(start),
                    total_page=total_page, page_size=page_size, prefix='/account/%s/image_article/single?' % aid,
                    index='material', top='image_article', articles=articles)


class ImageArticleGroupHandler(AccountBaseHandler):
    """查看多条图文列表"""

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        total = self.image_article_manager.get_image_article_group_count_by_aid(self.account.aid)
        total_page = math.ceil(float(total) / page_size)
        articles = self.image_article_manager.list_multi_image_article(aid, start, page_size)
        self.render('account/material_image_article_multi.html', account=self.account, total=total, start=int(start),
                    total_page=total_page, page_size=page_size, prefix='/account/%s/image_article/multi?' % aid,
                    index='material', top='image_article', articles=articles)


class NewSingleImageArticleHandler(AccountBaseHandler):
    """新建单条图文"""

    def get(self, aid):
        """返回页面"""
        self.render('account/material_image_article_new_single.html', account=self.account,
                    index='material', top='image_article')

    def post(self, *args, **kwargs):
        """提交创建"""
        result = {'aid': self.account.aid}
        title = self.get_argument('title', None)
        summary = self.get_argument('summary', None)
        link = self.get_argument('link', None)
        image = self.get_argument('image', None)
        if not title or not link or not summary:
            result['r'] = 0
            result['error'] = u'参数不完整'
            self.write(result)
            self.finish()
            return
        self.image_article_manager.save_single_image_article(title, summary, link, image, self.account.aid)
        result['r'] = 1
        self.write(result)
        self.finish()
        return


class EditSingleImageArticleHandler(AccountBaseHandler):
    """编辑单条图文消息"""

    def get(self, aid, iid):
        image_article = self.image_article_manager.get_image_article_by_id(iid)
        if image_article.aid != self.account.aid:
            raise HTTPError(404)
        self.render('account/material_image_article_new_single.html', account=self.account,
                    index='material', top='image_article', ia=image_article)

    def post(self, *args, **kwargs):
        aid = self.account.aid
        _id = int(args[1])
        title = self.get_argument('title', None)
        summary = self.get_argument('summary', None)
        image = self.get_argument('image', None)
        link = self.get_argument('link', None)
        image_article = self.image_article_manager.get_image_article_by_id(_id)
        if image_article.aid != self.account.aid:
            raise HTTPError(404)
        self.image_article_manager.update_single_image_article(title, summary, link, image, _id, aid)
        self.write({'r': 1, 'aid': aid})
        self.finish()
        return


class NewMultiImageArticleHandler(AccountBaseHandler):
    """新建多条图文"""

    def get(self, aid):
        self.render('account/material_image_article_new_multi.html', account=self.account,
                    index='material', top='image_article')

    def post(self, *args, **kwargs):
        aid = self.account.aid
        result = {'r': 0, 'aid': aid}
        params = self.get_argument('params', None)
        if not params:
            result['error'] = u'参数不正确'
            self.write(result)
            self.finish()
            return
        params = simplejson.loads(params, encoding='utf-8')
        id_list = []
        title = ''
        for index, param in enumerate(params):
            _title = param['title']
            _link = param['link']
            _image = param['image']
            if len(_image) == 0:
                _image = None
            if index == 0:
                title = _title
            _id = self.image_article_manager.save_single_image_article_with_type(_title, None, _link, _image, aid)
            id_list.append(_id)
        self.image_article_manager.save_multi_image_article(id_list[0] if len(id_list) > 0 else 0,
                                                            id_list[1] if len(id_list) > 1 else 0,
                                                            id_list[2] if len(id_list) > 2 else 0,
                                                            id_list[3] if len(id_list) > 3 else 0,
                                                            id_list[4] if len(id_list) > 4 else 0,
                                                            title, aid)
        result['r'] = 1
        self.write(result)
        self.finish()
        return


class EditMultiImageArticleHandler(AccountBaseHandler):
    """编辑多条图文"""

    def get(self, aid, iid):
        group = self.image_article_manager.get_multi_image_article_by_id(iid)
        if not group:
            raise HTTPError(404, 'image article not exists')
        id_list = [group.id1, group.id2, group.id3, group.id4, group.id5]
        id_list = filter(lambda a: a != 0, id_list)
        article_list = []
        for _id in id_list:
            article_list.append(self.image_article_manager.get_image_article_by_id(_id))
        self.render('account/material_image_article_new_multi.html', account=self.account,
                    index='material', top='image_article', article_list=article_list, more=(5 - len(id_list)))

    def post(self, *args, **kwargs):
        aid = self.account.aid
        iid = args[1]
        multi_article = self.image_article_manager.get_multi_image_article_by_id(iid)
        if not multi_article or multi_article.aid != aid:
            raise HTTPError(404)
        result = {'r': 0, 'aid': aid}
        params = self.get_argument('params', None)
        if not params:
            result['error'] = u'参数不正确'
            self.write(result)
            self.finish()
            return
        params = simplejson.loads(params, encoding='utf-8')
        id_list = []
        title = ''
        for index, param in enumerate(params):
            _id = int(param['id'])
            print _id
            _title = param['title']
            _link = param['link']
            _image = param['image']
            if len(_image) == 0:
                _image = None
            if index == 0:
                title = _title
            if _id:
                self.image_article_manager.update_single_image_article(_title, None, _link, _image, _id, aid)
            else:
                _id = self.image_article_manager.save_single_image_article_with_type(_title, None, _link, _image, aid)
            id_list.append(_id)
        self.image_article_manager.update_multi_image_article(id_list[0] if len(id_list) > 0 else 0,
                                                              id_list[1] if len(id_list) > 1 else 0,
                                                              id_list[2] if len(id_list) > 2 else 0,
                                                              id_list[3] if len(id_list) > 3 else 0,
                                                              id_list[4] if len(id_list) > 4 else 0,
                                                              title, iid)
        result['r'] = 1
        self.write(result)
        self.finish()
        return


class ArticleHandler(AccountBaseHandler):
    """所有文章列表"""

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        articles = self.article_manager.get_article(aid, start, page_size)
        total = self.article_manager.get_article_count_by_aid(aid)
        total_page = math.ceil(float(total) / page_size)
        self.render('account/material_article.html', account=self.account, total=total, start=int(start),
                    total_page=total_page, page_size=page_size, prefix='/account/%s/article?' % aid, articles=articles,
                    index='material', top='article')


class EditArticleHandler(AccountBaseHandler):
    """编辑文章"""

    def get(self, aid, slug):
        article = self.article_manager.get_article_by_slug(slug)
        if not article:
            raise HTTPError(404)
        if article.aid != aid:
            raise HTTPError(404)
        self.render('account/material_article_edit.html', account=self.account, index='material', top='article',
                    article=article)

    def post(self, *args, **kwargs):
        """保存修改"""
        result = {'r': 1, 'aid': self.account.aid}
        title = self.get_argument('title', '')
        content = self.get_argument('content', '')
        slug = self.get_argument('slug', '')
        article = self.article_manager.get_article_by_slug(slug)
        if not article:
            raise HTTPError(404)
        if article.aid != self.account.aid:
            raise HTTPError(404)
        self.article_manager.update_article(slug, title, content)
        self.write(result)
        self.finish()

    def delete(self, *args, **kwargs):
        """删除文章"""
        result = {'r': 1, 'aid': self.account.aid}
        slug = args[1]
        article = self.article_manager.get_article_by_slug(slug)
        if not article:
            raise HTTPError(404)
        if article.aid != self.account.aid:
            raise HTTPError(404)
        self.article_manager.delete_article(slug)
        self.write(result)
        self.finish()


class NewArticleHandler(AccountBaseHandler):
    """新建文章"""

    def get(self, aid):
        """新建文章页面"""
        self.render('account/material_article_new.html', account=self.account, index='material', top='article')

    def post(self, *args, **kwargs):
        result = {'r': 1}
        title = self.get_argument('title', '')
        content = self.get_argument('content', '')
        slug = key_util.generate_hexdigits_lower(8)
        while self.article_manager.exists_article(slug):
            slug = key_util.generate_hexdigits_lower(8)
        self.article_manager.save_article(slug, title, content, self.account.aid)
        result['aid'] = self.account.aid
        self.write(result)
        self.finish()
        return


class ImageArticlePreviewHandler(BaseHandler):
    """预览单条图文消息"""
    image_article_manager = None

    def prepare(self):
        self.image_article_manager = ImageArticleManager(self.db)

    def get(self, article_id):
        image_article = self.image_article_manager.get_image_article_by_id(article_id)
        if not image_article:
            raise HTTPError(404, 'image article not exists')
        self.render('article/image_article_preview.html', image_article=image_article)


class ImageArticleGroupPreviewHandler(BaseHandler):
    """预览多条图文消息"""
    image_article_manager = None

    def prepare(self):
        self.image_article_manager = ImageArticleManager(self.db)

    def get(self, article_id):
        image_article_group = self.image_article_manager.get_multi_image_article_by_id(article_id)
        if not image_article_group:
            raise HTTPError(404, 'image article not exists')
        main_article = self.image_article_manager.get_image_article_by_id(image_article_group.id1)
        id_list = [image_article_group.id2, image_article_group.id3, image_article_group.id4, image_article_group.id5]
        id_list = filter(lambda a: a != 0, id_list)
        article_list = []
        for _id in id_list:
            article_list.append(self.image_article_manager.get_image_article_by_id(_id))
        self.render('article/image_article_group_preview.html', main_article=main_article, article_list=article_list)


class DeleteMaterialHandler(AccountBaseHandler):
    """删除素材的handler"""

    def post(self, *args, **kwargs):
        result = {'r': 1}
        _type = self.get_argument('type', None)
        _id = self.get_argument('id', 0)
        if not _type or not _id:
            result['r'] = 0
            result['error'] = '参数不正确'
            self.write(result)
            self.finish()
            return
        if _type == 'single':
            self.image_article_manager.remove_single_image_article(_id, self.account.aid)
        if _type == 'multi':
            self.image_article_manager.remove_image_article_grouo(_id, self.account.aid)
        self.write(result)
        self.finish()
        return


handlers = [
    (r'/image_article/([^/]+)/preview', ImageArticlePreviewHandler),
    (r'/image_article_group/([^/]+)/preview', ImageArticleGroupPreviewHandler),
    (r'/account/([^/]+)/image_article/single', ImageArticleHandler),
    (r'/account/([^/]+)/image_article/multi', ImageArticleGroupHandler),
    (r'/account/([^/]+)/image_article/new/single', NewSingleImageArticleHandler),
    (r'/account/([^/]+)/image_article/new/multi', NewMultiImageArticleHandler),
    (r'/account/([^/]+)/image_article/single/([^/]+)/edit', EditSingleImageArticleHandler),
    (r'/account/([^/]+)/image_article/multi/([^/]+)/edit', EditMultiImageArticleHandler),
    (r'/account/([^/]+)/article', ArticleHandler),
    (r'/account/([^/]+)/article/new', NewArticleHandler),
    (r'/account/([^/]+)/article/([^/]+)/edit', EditArticleHandler),
    (r'/account/([^/]+)/delete_material', DeleteMaterialHandler),
]