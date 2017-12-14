#!/usr/bin/env python
from setuptools import setup, find_packages


def README():
    with open('README.rst') as f:
        return f.read()


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
