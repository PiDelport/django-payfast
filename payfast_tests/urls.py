import django
from django.conf.urls import url, include
from django.contrib import admin

import payfast.urls


if django.VERSION < (1, 7):
    admin.autodiscover()


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^payfast/', include(payfast.urls)),
]
