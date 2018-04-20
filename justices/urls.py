from django.conf.urls import url
from justices import views

urlpatterns = [
    url(r'^justices/$', views.index, name='justices'),
    url(r'^justices/(.*)$', views.redirect, name='justices'),
]
