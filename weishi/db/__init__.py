#coding:utf-8

__author__ = 'young'


def connect():
    """连接数据库"""
    from weishi.db import mysql

    mysql.connect()


class _Connection(dict):
    def __init__(self):
        self["_db"] = {"mysql": None}

    def __getattr__(self, key):
        if key in self["_db"]:
            return self["_db"][key]
        else:
            raise AttributeError

    def __setattr__(self, key, value):
        if key in self["_db"]:
            self["_db"][key] = value
        else:
            raise AttributeError


conn = _Connection()