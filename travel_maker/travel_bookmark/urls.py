from django.conf.urls import url

from travel_maker.travel_bookmark.views import TravelBookmarkCreateView, TravelBookmarkDeleteView

urlpatterns = [
    url(r'^create/$', TravelBookmarkCreateView.as_view(), name='create'),
    url(r'^delete/(?P<pk>\d+)/$', TravelBookmarkDeleteView.as_view(), name='delete'),
]
