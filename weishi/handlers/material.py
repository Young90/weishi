#coding:utf-8
__author__ = 'young'

import string
import math

from weishi.libs import key_util
from weishi.handlers.account import AccountBaseHandler


class ImageArticleHandler(AccountBaseHandler):
    """图文管理"""

    def get(self, aid):
        start = self.get_argument('start', 0)
        page_size = 10
        total = 5
        total_page = 1
        self.render('account/material_image_article.html', account=self.account, total=total, start=int(start),
                    total_page=total_page, page_size=page_size, prefix='/account/%s/image_article' % aid,
                    index='material', top='image_article')


class NewSingleImageArticleHandler(AccountBaseHandler):
    """新建单条图文"""

    def get(self, aid):
        self.render('account/material_image_article_new_single.html', account=self.account,
                    index='material', top='image_article')


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


handlers = [
    (r'/account/([^/]+)/image_article', ImageArticleHandler),
    (r'/account/([^/]+)/image_article/new/single', NewSingleImageArticleHandler),
    (r'/account/([^/]+)/image_article/new/multi', NewMultiImageArticleHandler),
    (r'/account/([^/]+)/article', ArticleHandler),
    (r'/account/([^/]+)/article/new', NewArticleHandler),
]