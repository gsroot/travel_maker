from django.conf.urls import url

from travel_maker.travel_info.views import TravelInfoListView, TravelInfoDetailView, TravelInfoList, BlogList, \
    NearbySpotInfoList, NearbySpotInfoListView, BookmarkList

urlpatterns = [
    url(r'^$', TravelInfoListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', TravelInfoDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/nearby/$', NearbySpotInfoListView.as_view(), name='nearby_list'),
    url(r'^api/$', TravelInfoList.as_view(), name='list_api'),
    url(r'^api/bookmarks/$', BookmarkList.as_view(), name='bookmark_list_api'),
    url(r'^api/(?P<pk>\d+)/nearbylist/$', NearbySpotInfoList.as_view(), name='nearby_list_api'),
    url(r'^api/(?P<pk>\d+)/blogs/$', BlogList.as_view(), name='blog_list_api'),
]
