from django.conf.urls import url
from subscribers import views

urlpatterns = [
    url(r'^signup$', views.sign_up, name='sign up'),
    url(r'^subscribe/(?P<hash_key>[\w{}.-]{20})$', views.subscribe, name='subscribe'),
    url(r'^unsubscribe/(?P<hash_key>[\w{}.-]{20})$', views.unsubscribe, name='unsubscribe'),
    url(r'^notifysubscribers', views.notify_subscribers, name='notify subscribers'),
]