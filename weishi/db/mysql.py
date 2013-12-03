#coding:utf-8
__author__ = 'young'

from torndb import Connection
from tornado.options import define, options
from tornado.ioloop import PeriodicCallback
from weishi.db import conn

define("host", default="localhost:3306", help="Main db url")
define("database", default="weishi")
define("user", default="root")
define("password", default="root")
define("recycle", default=4 * 3600)


def connect():
    conn.mysql = Connection(
        host=options.host,
        database=options.database,
        user=options.user,
        password=options.password,

    )

    # 每隔一段时间ping数据库
    PeriodicCallback(_ping_db, options.recycle * 1000).start()


def _ping_db():
    conn.mysql.query("show variables")