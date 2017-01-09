"""culturedata_proto URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from filebrowser.sites import site

from config.settings.base import MEDIA_URL, MEDIA_ROOT
from travel_maker.views import HomeView

urlpatterns = [
    url(r'^admin/filebrowser/', include(site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^accounts/profile/(?P<pk>\d+)/', include('travel_maker.account.urls', namespace='profile')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^travel-info/', include('travel_maker.travel_info.urls', namespace='travel_info')),
    url(r'^travel-review/', include('travel_maker.travel_review.urls', namespace='travel_review')),
    url(r'^travel-schedule/', include('travel_maker.travel_schedule.urls', namespace='travel_schedule')),
    url(r'^summernote/', include('django_summernote.urls')),
] + staticfiles_urlpatterns() + static(MEDIA_URL, document_root=MEDIA_ROOT)
