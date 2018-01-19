from __future__ import unicode_literals

import django
import os
import sys


# Turn timezone awareness violation warnings into errors, for development.
# See https://docs.djangoproject.com/en/stable/topics/i18n/timezones/#code
import warnings
warnings.filterwarnings(
    'error',
    r'DateTimeField .* received a naive datetime',
    RuntimeWarning,
    r'django\.db\.models\.fields',
)


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
join = lambda p: os.path.abspath(os.path.join(PROJECT_ROOT, p))  # noqa: E731

# use package from the folder above, not the installed version
sys.path.insert(0, join('..'))

# ===== payfast settings ====

PAYFAST_MERCHANT_ID = '10000100'
PAYFAST_MERCHANT_KEY = '46f0cd694581a'

PAYFAST_URL_BASE = 'http://example.com/'

# ===========================

DEBUG = True

ADMINS = ()
MANAGERS = ADMINS

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join('db.sqlite'),  # Or path to database file if using sqlite3.
    }
}

USE_TZ = True
TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
MEDIA_ROOT = join('media')
MEDIA_URL = '/media/'
SECRET_KEY = '5mcs97ar-(nnxjok67290+0^sr!e(ax=x$2-!8dqy25ff-l1*a='

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# Django 1.10 migrates MIDDLEWARE_CLASSES to MIDDLEWARE
if django.VERSION < (1, 10):
    MIDDLEWARE_CLASSES = MIDDLEWARE
    del MIDDLEWARE

ROOT_URLCONF = 'urls'

# Django 1.8 migrates TEMPLATE_* to TEMPLATES
if django.VERSION < (1, 8):
    TEMPLATE_DEBUG = DEBUG
    TEMPLATE_LOADERS = [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]
    TEMPLATE_DIRS = [
        join('templates'),
    ]
else:
    TEMPLATES = [
        {
            "BACKEND": 'django.template.backends.django.DjangoTemplates',
            'DIRS': (join('templates'),),
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                ],
            }
        }
    ]


INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'payfast',
]
