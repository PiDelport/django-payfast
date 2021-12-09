from django.urls import re_path

from payfast.views import notify_handler


urlpatterns = [
    re_path(r'^notify/$', notify_handler, name='payfast_notify'),
]
