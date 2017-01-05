from django.conf.urls import url

from travel_maker.travel_info.views import TravelInfoLV, TravelInfoDV, TravelInfoList, BlogList, NearbyTravelInfoList

urlpatterns = [
    url(r'^$', TravelInfoLV.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', TravelInfoDV.as_view(), name='detail'),
    url(r'^api/$', TravelInfoList.as_view(), name='list_api'),
    url(r'^api/(?P<pk>\d+)/nearby/$', NearbyTravelInfoList.as_view(), name='nearby_list_api'),
    url(r'^api/(?P<pk>\d+)/blogs/$', BlogList.as_view(), name='blog_list_api'),
]
