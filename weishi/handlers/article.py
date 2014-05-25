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
        article = self._get_article_by_slug(slug)
        if not article:
            raise HTTPError(404)
        openid = self.get_argument('i', '')
        self.render('article/article.html', article=article, i=openid)


class ArticleTemplateHandler(BaseHandler):

    def get(self, slug):
        template = self.db.get('select * from t_template where slug = %s', slug)
        if not template:
            raise HTTPError(404)
        openid = self.get_argument('i', '')
        temp_file = 'article/sub_temp_%s.html' % template.type
        lists = self.db.query('select * from t_template_list where slug = %s', slug)
        self.render(temp_file, i=openid, t=template, lists=lists)


handlers = [
    (r'/article/template/([^/]+)', ArticleTemplateHandler),
    (r'/article/([^/]+)', ArticleHandler),
]