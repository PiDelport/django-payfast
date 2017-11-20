import django

from payfast.views import notify_handler

if django.VERSION < (1, 4):
    from django.conf.urls.defaults import url
else:
    from django.conf.urls import url


urlpatterns = [
    url('^notify/$', notify_handler, name='payfast_notify'),
]
