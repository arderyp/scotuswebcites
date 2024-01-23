from django.urls import re_path
from justices import views

urlpatterns = [
    re_path(r'^justices/$', views.index, name='justices'),
    re_path(r'^justices/(.*)$', views.redirect, name='justices'),
]
