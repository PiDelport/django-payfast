#!/usr/bin/env python
from distutils.core import setup

setup(
    name='django-payfast',
    version='0.2.0',
    author='Mikhail Korobov',
    author_email='kmike84@gmail.com',

    packages=['payfast', 'payfast.migrations'],

    url='http://bitbucket.org/kmike/django-payfast/',
    download_url = 'http://bitbucket.org/kmike/django-payfast/get/tip.gz',
    license = 'MIT license',
    description = 'A pluggable Django application for integrating payfast.co.za payment system.',
    long_description = open('README.rst').read().decode('utf8'),

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
