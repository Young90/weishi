#coding:utf-8
__author__ = 'young'


def dicttoxml(obj, root=None):
    if root:
        result = '<%s>' % root
    else:
        result = ''
    for key, value in obj.items():
        if isinstance(value, basestring):
            result += '<%s><![CDATA[%s]]></%s>' % (key, value, key)
        elif isinstance(value, int):
            result += '<%s>%s</%s>' % (key, value, key)
        elif isinstance(value, list):
            result += '<%s>%s</%s>' % (key, dicttoxml(value, root=value), key)
    if root:
        result += '</%s>' % root
    return result