#coding:utf-8
__author__ = 'young'

import math

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
        total = 5
        total_page = 1
        articles = self.image_article_manager.list_single_image_article(aid, start, page_size)
        self.render('account/material_image_article_single.html', account=self.account, total=total, start=int(start),
                    total_page=total_page, page_size=page_size, prefix='/account/%s/image_article_single' % aid,
                    index='material', top='image_article', articles=articles)


class ImageArticleGroupHandler(AccountBaseHandler):
    """多条图文管理"""

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        total = 5
        total_page = 1
        self.render('account/material_image_article_multi.html', account=self.account, total=total, start=int(start),
                    total_page=total_page, page_size=page_size, prefix='/account/%s/image_article_multi' % aid,
                    index='material', top='image_article')


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


class NewMultiImageArticleHandler(AccountBaseHandler):
    """新建多条图文"""

    def get(self, aid):
        self.render('account/material_image_article_new_multi.html', account=self.account,
                    index='material', top='image_article')


class ArticleHandler(AccountBaseHandler):
    """所有文章列表"""

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        articles = self.article_manager.get_article(aid, start, page_size)
        total = self.article_manager.get_article_count_by_aid(aid)
        total_page = math.ceil(float(total) / page_size)
        self.render('account/material_article.html', account=self.account, total=total, start=int(start),
                    total_page=total_page, page_size=page_size, prefix='/account/%s/article' % aid, articles=articles,
                    index='material', top='article')


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
        self.render('article/image_article_preview.html', image_article=image_article[0])


class ImageArticleGroupPreviewHandler(BaseHandler):
    """预览多条图文消息"""
    image_article_manager = None

    def prepare(self):
        self.image_article_manager = ImageArticleManager(self.db)

    def get(self, article_id):
        image_article_group = self.image_article_manager.get_multi_image_article_by_id(article_id)
        if not image_article_group:
            raise HTTPError(404, 'image article not exists')
        image_article_group = image_article_group[0]
        main_article = self.image_article_manager.get_image_article_by_id(image_article_group.id1)
        id_list = [image_article_group.id2, image_article_group.id3, image_article_group.id4, image_article_group.id5]
        id_list = filter(lambda a: a != 0, id_list)
        article_list = self.image_article_manager.get_image_article_by_id_list(id_list)
        self.render('article/image_article_group_preview.html', main_article=main_article, article_list=article_list)


handlers = [
    (r'/image_article/([^/]+)/preview', ImageArticlePreviewHandler),
    (r'/image_article_group/([^/]+)/preview', ImageArticleGroupPreviewHandler),
    (r'/account/([^/]+)/image_article/single', ImageArticleHandler),
    (r'/account/([^/]+)/image_article/multi', ImageArticleGroupHandler),
    (r'/account/([^/]+)/image_article/new/single', NewSingleImageArticleHandler),
    (r'/account/([^/]+)/image_article/new/multi', NewMultiImageArticleHandler),
    (r'/account/([^/]+)/article', ArticleHandler),
    (r'/account/([^/]+)/article/new', NewArticleHandler),
]