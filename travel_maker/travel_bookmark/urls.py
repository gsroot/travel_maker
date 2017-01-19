from django.conf.urls import url

from travel_maker.travel_bookmark.views import TravelBookmarkCreateView, TravelBookmarkDeleteView, \
    ScheduleBookmarkCreateView, ScheduleBookmarkDeleteView

urlpatterns = [
    url(r'^create/$', TravelBookmarkCreateView.as_view(), name='create'),
    url(r'^delete/(?P<pk>\d+)/$', TravelBookmarkDeleteView.as_view(), name='delete'),
    url(r'^schedule/create/$', ScheduleBookmarkCreateView.as_view(), name='schedule_create'),
    url(r'^schedule/delete/(?P<pk>\d+)/$', ScheduleBookmarkDeleteView.as_view(), name='schedule_delete'),
]
