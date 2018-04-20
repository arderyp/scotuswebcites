from django.conf.urls import url
from citations import views

urlpatterns = [
    url(r'^citations/$', views.index, name='citations'),
    url(r'^citations/(\d+)$', views.opinion_citations, name='opinion citations'),
    url(r'^citations/(\w+)$', views.justice_opinions_citations, name='justice opinions citations'),
    url(r'^citations/verify/(\d+)$', views.verify, name='opinion citations'),
    url(r'^citations/verify/(\w+)?$', views.redirect, name='redirect'),
]
