from django.conf.urls import url

from travel_maker.travel_bookmark.views import TravelBookmarkListView, TravelBookmarkCreateView, \
    TravelBookmarkDeleteView

urlpatterns = [
    url(r'^$', TravelBookmarkListView.as_view(), name='list'),
    url(r'^create/$', TravelBookmarkCreateView.as_view(), name='create'),
    url(r'^delete/(?P<pk>\d+)/$', TravelBookmarkDeleteView.as_view(), name='delete'),
]
