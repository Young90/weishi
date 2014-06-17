# coding:utf-8
__author__ = 'houxiaohou'

import datetime


def today_start_date():
    now = datetime.now()
    start = datetime(year=now.year, month=now.month, day=now.day, hour=0, minute=0, second=0)
    return start