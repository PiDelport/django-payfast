from django.conf.urls.defaults import *
from payfast.views import notify_handler

urlpatterns = patterns('',
    url('^notify/$', notify_handler, name='payfast_notify'),
)
