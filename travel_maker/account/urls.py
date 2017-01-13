from django.conf.urls import url

from travel_maker.account.views import ProfileHomeView, ProfilePasswordChangeView, ProfileDeleteView, \
    ProfileScheduleListView, ProfileBookmarkListView

urlpatterns = [
    url(r'^$', ProfileHomeView.as_view(), name='home'),
    url(r'^password-change/$', ProfilePasswordChangeView.as_view(), name='password_change'),
    url(r'^delete/$', ProfileDeleteView.as_view(), name='delete'),
    url(r'^schedule-list/$', ProfileScheduleListView.as_view(), name='schedule_list'),
    url(r'^bookmark-list/$', ProfileBookmarkListView.as_view(), name='bookmark_list'),
]
