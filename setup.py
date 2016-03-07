#!/usr/bin/python3 -tt

from setuptools import setup
import os.path

setup(
    name = 'provokator',
    version = '1',
    author = 'NTK',
    description = ('smstools-http-api auditing companion'),
    license = 'MIT',
    keywords = 'sms api audit',
    url = 'http://github.com/techlib/provokator',
    include_package_data = True,
    package_data = {
        '': ['*.png', '*.js', '*.png', '*.html'],
    },
    packages = [
        'provokator',
        'provokator.site',
    ],
    classifiers = [
        'License :: OSI Approved :: MIT License',
    ],
    scripts = ['provokator-daemon']
)


# vim:set sw=4 ts=4 et:
# -*- coding: utf-8 -*-
