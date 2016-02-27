from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^justices/$', 'justices.views.index', name='justices'),

    # Redirects
    url(r'^justices/(.*)$', 'justices.views.redirect', name='justices'),
]
