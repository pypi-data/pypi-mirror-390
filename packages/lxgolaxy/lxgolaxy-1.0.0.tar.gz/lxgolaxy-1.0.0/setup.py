#-*- coding:utf-8 -*-
# @Author  : lx

from setuptools import setup,find_packages

with open("README.rst", "r") as f:
  long_description = f.read()

setup(
    name = 'lxgolaxy',
    url='https://pypi.org/project/lxgolaxy',
    version = '1.0.0',
    description='Private configuration information !',
    long_description=long_description,
    packages = ['lxgolaxy'],
    author = 'lx',
    author_email = '125066648@qq.com',
    platforms = ["all"],
    install_requires=["wheel"],
    )


# python setup.py sdist bdist_wheel
# twine upload dist/*