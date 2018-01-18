#!/usr/bin/env python
import sys
from setuptools import setup, find_packages


def README():
    with open('README.rst') as f:
        return f.read()


_PYTHON_2_BACKPORTS = ['ipaddress'] if sys.version_info < (3,) else []


setup(
    name='django-payfast',
    # Version automatically from tags using setuptools-scm
    use_scm_version=True,

    maintainer='Pi Delport',
    maintainer_email='pjdelport@gmail.com',

    packages=find_packages(exclude=['payfast_tests']),

    setup_requires=['setuptools-scm'],

    install_requires=[
        'six',
        'Django',

        'typing; python_version<"3.5"',
    ] + _PYTHON_2_BACKPORTS,

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
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
