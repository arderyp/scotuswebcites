from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^opinions/$', 'opinions.views.index', name='opinions'),
    url(r'^opinions/(\w+)$', 'opinions.views.justice_opinions', name='justice opinions'),

    # Redirects
    url(r'^opinions/(\d+)$', 'opinions.views.redirect', name='redirect'),
]
