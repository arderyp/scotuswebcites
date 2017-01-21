from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'scotuswebcites.views.overview', name='overview'),
    url(r'^data/$', 'scotuswebcites.views.data', name='data'),
    url(r'^csv$', 'scotuswebcites.views.download_csv', name='csv'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout$', 'scotuswebcites.views.logout', name='logout'),
    url('', include('citations.urls')),
    url('', include('opinions.urls')),
    url('', include('justices.urls')),
    url('', include('subscribers.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
