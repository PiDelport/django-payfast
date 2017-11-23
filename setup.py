#!/usr/bin/env python
from setuptools import setup, find_packages


def README():
    with open('README.rst') as f:
        return f.read()


setup(
    name='django-payfast',
    version='0.3.dev',
    maintainer='Pi Delport',
    maintainer_email='pjdelport@gmail.com',

    packages=find_packages(exclude=['payfast_tests']),

    install_requires=[
        'Django',
    ],

    url='https://github.com/pjdelport/django-payfast',
    license='MIT license',
    description='A pluggable Django application for integrating payfast.co.za payment system.',
    long_description=README(),

    classifiers=(
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
