#coding:utf-8
__author__ = 'young'

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
    """图文管理"""

    def get(self, aid):
        self.render('account/material_image_article_new_single.html', account=self.account,
                    index='material', top='image_article')


class NewMultiImageArticleHandler(AccountBaseHandler):
    """图文管理"""

    def get(self, aid):
        self.render('account/material_image_article_new_multi.html', account=self.account,
                    index='material', top='image_article')


class ArticleHandler(AccountBaseHandler):
    """图片素材管"""

    def get(self, aid):
        self.render('account/material_article.html', account=self.account, index='material', top='article')


handlers = [
    (r'/account/([^/]+)/image_article', ImageArticleHandler),
    (r'/account/([^/]+)/image_article/new/single', NewSingleImageArticleHandler),
    (r'/account/([^/]+)/image_article/new/multi', NewMultiImageArticleHandler),
    (r'/account/([^/]+)/article', ArticleHandler),
]