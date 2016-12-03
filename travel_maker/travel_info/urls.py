from django.conf.urls import url

from travel_maker.travel_info.views import TravelInfoLV, TravelInfoDV

urlpatterns = [
    url(r'^$', TravelInfoLV.as_view(), name='list'),
    url(r'^(?P<id>[\d]+)/$', TravelInfoDV.as_view(), name='detail'),
]
