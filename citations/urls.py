from django.urls import re_path
from citations import views

urlpatterns = [
    re_path(r'^citations/$', views.index, name='citations'),
    re_path(r'^citations/(\d+)$', views.opinion_citations, name='opinion citations'),
    re_path(r'^citations/(\w+)$', views.justice_opinions_citations, name='justice opinions citations'),
    re_path(r'^citations/verify/(\d+)$', views.verify, name='opinion citations'),
    re_path(r'^citations/verify/(\w+)?$', views.redirect, name='redirect'),
]
