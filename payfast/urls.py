from django.conf.urls import url

from payfast.views import notify_handler


urlpatterns = [
    url('^notify/$', notify_handler, name='payfast_notify'),
]
