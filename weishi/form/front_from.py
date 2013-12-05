#coding:utf-8
__author__ = 'young'

from wtforms_tornado import Form
from wtforms import StringField, validators


class AccountForm(Form):
    """
    添加微信公众账号的表单校验
    """
    app_name = StringField("app_name", validators=[
        validators.input_required(message=u'公众账号名称不能为空'),
        validators.length(max=30, message=u'公众账号名称过长'),
    ])
    app_id = StringField("app_id", validators=[
        validators.input_required(message=u'公众账号id不能为空'),
        validators.length(min=10, max=20, message=u'公众账号id长度不正确'),
    ])
    app_account = StringField("app_account", validators=[
        validators.input_required(message=u'微信号不能为空'),
        validators.length(max=100, message=u'微信号长度过长'),
    ])