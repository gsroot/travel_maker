from django.conf.urls import url

from travel_maker.travel_schedule.views import TravelScheduleCreateView, TravelScheduleListView, \
    TravelScheduleDetailView, TravelScheduleDeleteView, TravelScheduleUpdateView, \
    TravelCalendarUpdate, TravelCalendarUpdateView, TravelScheduleUpdate

urlpatterns = [
    url(r'^$', TravelScheduleListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', TravelScheduleDetailView.as_view(), name='detail'),
    url(r'^create/$', TravelScheduleCreateView.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)$', TravelScheduleUpdateView.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', TravelScheduleDeleteView.as_view(), name='delete'),
    url(r'^update_calendar/(?P<pk>\d+)/$', TravelCalendarUpdateView.as_view(), name='calendar_update'),
    url(r'^update/api/(?P<pk>\d+)/$', TravelScheduleUpdate.as_view(), name='update_api'),
    url(r'^update_calendar/api/(?P<pk>\d+)/$', TravelCalendarUpdate.as_view(), name='calendar_update_api'),
]
