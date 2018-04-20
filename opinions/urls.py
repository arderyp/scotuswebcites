from django.conf.urls import url
from opinions import views

urlpatterns = [
    url(r'^opinions/$', views.index, name='opinions'),
    url(r'^opinions/(\w+)$', views.justice_opinions, name='justice opinions'),
    url(r'^opinions/(\d+)$', views.redirect, name='redirect'),
]
