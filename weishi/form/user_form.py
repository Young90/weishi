#coding:utf-8
__author__ = 'young'

from wtforms import StringField, PasswordField, validators
from wtforms_tornado import Form
from wtforms import ValidationError


def username_check(form, field):
    length = len(field.data)
    utf_len = len(field.data.encode('utf-8'))
    length += (utf_len - length) / 2
    if length < 4 or length > 20:
        raise ValidationError(u'用户名长度在4-20之间，中文长度为2')


def mobile_check(form, field):
    if field.data and field.data != '':
        if len(field.data) != 11:
            raise ValidationError(u'手机号码不正确')


class SignupForm(Form):
    username = StringField(u'username', validators=[
        validators.input_required(message=u'用户名不能为空！'),
        username_check
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
    mobile = StringField(u'mobile', validators=[mobile_check])