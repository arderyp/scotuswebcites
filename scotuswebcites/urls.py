from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import re_path
from scotuswebcites import views


urlpatterns = [
    re_path(r'^$', views.overview, name='overview'),
    re_path(r'^data/$', views.data, name='data'),
    re_path(r'^csv$', views.download_csv, name='csv'),
    re_path(r'^logout$', views.logout, name='logout'),
    re_path(r'^login/$', LoginView.as_view(), name='login'),
    re_path('', include('citations.urls')),
    re_path('', include('opinions.urls')),
    re_path('', include('justices.urls')),
    re_path('', include('subscribers.urls')),
    re_path(r'^admin/', admin.site.urls),
]
