#coding:utf-8
__author__ = 'young'

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    install_requires=["tornado>=3.0",
                      "torndb>=0.1",
                      "qiniu",
                      "wtforms>1.0",
                      "wtforms-tornado>0",
    ],
)