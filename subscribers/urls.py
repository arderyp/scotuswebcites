from django.conf.urls import url

urlpatterns = [
    url(r'^signup$', 'subscribers.views.sign_up', name='sign up'),
    url(r'^subscribe/(?P<hash_key>[\w{}.-]{20})$', 'subscribers.views.subscribe', name='subscribe'),
    url(r'^unsubscribe/(?P<hash_key>[\w{}.-]{20})$', 'subscribers.views.unsubscribe', name='unsubscribe'),
    url(r'^notifysubscribers', 'subscribers.views.notify_subscribers', name='notify subscribers'),
]