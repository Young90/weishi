#coding:utf-8
__author__ = 'young'

from wtforms_tornado import Form
from wtforms import StringField, validators


class AccountForm(Form):
    """
    添加微信公众账号的表单校验
    """
    wei_name = StringField('wei_name', validators=[
        validators.input_required(message=u'公众账号名称不能为空'),
        validators.length(max=30, message=u'公众账号名称过长'),
    ])
    wei_id = StringField('wei_id', validators=[
        validators.input_required(message=u'公众账号id不能为空'),
        validators.length(max=20, message=u'公众账号id长度过长'),
    ])
    wei_account = StringField('wei_account', validators=[
        validators.input_required(message=u'微信号不能为空'),
        validators.length(max=100, message=u'微信号长度过长'),
    ])