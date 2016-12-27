from django.conf.urls import url

from travel_maker.travel_info.views import TravelInfoLV, TravelInfoDV, TravelInfoList

urlpatterns = [
    url(r'^$', TravelInfoLV.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', TravelInfoDV.as_view(), name='detail'),
    url(r'^api/$', TravelInfoList.as_view(), name='list_api'),
]
