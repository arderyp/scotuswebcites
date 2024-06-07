from django.urls import re_path
from subscribers import views

urlpatterns = [
    # re_path(r'^signup$', views.sign_up, name='sign up'),
    # re_path(r'^subscribe/(?P<hash_key>[\w{}.-]{20})$', views.subscribe, name='subscribe'),
    re_path(r'^unsubscribe/(?P<hash_key>[\w{}.-]{20})$', views.unsubscribe, name='unsubscribe'),
    # re_path(r'^notifysubscribers', views.notify_subscribers, name='notify subscribers'),
]