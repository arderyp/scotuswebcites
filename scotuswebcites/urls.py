from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login
from scotuswebcites import views


urlpatterns = [
    url(r'^$', views.overview, name='overview'),
    url(r'^data/$', views.data, name='data'),
    url(r'^csv$', views.download_csv, name='csv'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^login/$', login, name='login'),
    url('', include('citations.urls')),
    url('', include('opinions.urls')),
    url('', include('justices.urls')),
    url('', include('subscribers.urls')),
    url(r'^admin/', admin.site.urls),
]
