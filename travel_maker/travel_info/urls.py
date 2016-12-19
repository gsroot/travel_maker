from django.conf.urls import url
from django.views.generic import ArchiveIndexView

from travel_maker.travel_info.views import TravelInfoLV, TravelInfoDV

urlpatterns = [
    url(r'^$', TravelInfoLV.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', TravelInfoDV.as_view(), name='detail'),
]
