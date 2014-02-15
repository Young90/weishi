#coding:utf-8
__author__ = 'Young'

from tornado.web import HTTPError

from weishi.libs.handler import BaseHandler


class ArticleHandler(BaseHandler):
    """查看文章的handler"""

    def _get_article_by_slug(self, slug):
        """根据slug查询数据库，获取article"""
        return self.db.get('select * from t_article where slug = %s and auto_response = 0', slug)

    def get(self, slug):
        """访问地址时，返回相关文章"""
        if not slug:
            raise HTTPError(404)
            return
        article = self._get_article_by_slug(slug)
        if not article:
            raise HTTPError(404)
            return
        self.render('article/article.html', article=article)


handlers = [
    (r'/article/([^/]+)', ArticleHandler)
]