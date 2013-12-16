#coding:utf-8
__author__ = 'young'

from torndb import Connection
from tornado.options import define, options
from tornado.ioloop import PeriodicCallback
from weishi.db import conn
from weishi import conf

define("host", default=conf.mysql_host, help="Main db url")
define("database", default=conf.mysql_database)
define("user", default=conf.mysql_user)
define("password", default=conf.mysql_password)
define("recycle", default=4 * 3600)


def connect():
    conn.mysql = Connection(
        host=options.host,
        database=options.database,
        user=options.user,
        password=options.password
    )

    # 每隔一段时间ping数据库
    PeriodicCallback(_ping_db, options.recycle * 1000).start()


def _ping_db():
    conn.mysql.query("show variables")