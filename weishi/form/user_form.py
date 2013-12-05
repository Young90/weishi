#coding:utf-8
__author__ = 'young'

from wtforms import StringField, PasswordField, validators
from wtforms_tornado import Form


class SignupForm(Form):
    username = StringField(u'username', validators=[
        validators.input_required(message=u'用户名不能为空！'),
    ])
    email = StringField(u'email', validators=[
        validators.input_required(message=u'邮箱不能为空！'),
        validators.email(message=u'邮箱格式不正确！'),
        validators.length(min=4, max=40, message=u'邮箱长度不正确！')
    ])
    password = PasswordField(u'password', validators=[
        validators.input_required(message=u'密码不能为空！'),
        validators.length(min=6, max=20, message=u'密码长度在6-20之间！')
    ])
    mobile = StringField(u'mobile', validators=[
        validators.length(min=11, max=11, message=u'手机号不正确！')
    ])