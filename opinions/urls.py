from django.urls import re_path
from opinions import views

urlpatterns = [
    re_path(r'^opinions/$', views.index, name='opinions'),
    re_path(r'^opinions/(\w+)$', views.justice_opinions, name='justice opinions'),
    re_path(r'^opinions/(\d+)$', views.redirect, name='redirect'),
]
