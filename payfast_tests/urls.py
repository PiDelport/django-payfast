import django
from django.urls import re_path, include
from django.contrib import admin

import payfast.urls


if django.VERSION < (1, 7):
    admin.autodiscover()


urlpatterns = [
    re_path(
        r"^admin/",
        admin.site.urls,
    ),
    re_path(
        r'^payfast/',
        include(payfast.urls),
    ),
]
