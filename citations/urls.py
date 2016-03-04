from django.conf.urls import url

urlpatterns = [
    url(r'^citations/$', 'citations.views.index', name='citations'),
    url(r'^citations/(\d+)$', 'citations.views.opinion_citations', name='opinion citations'),
    url(r'^citations/(\w+)$', 'citations.views.justice_opinions_citations', name='justice opinions citations'),
    url(r'^citations/verify/(\d+)$', 'citations.views.verify', name='opinion citations'),
    
    # Redirects
    url(r'^citations/verify/(\w+)?$', 'citations.views.redirect', name='redirect'),
]
