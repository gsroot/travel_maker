from django.conf.urls import url

from travel_maker.account.views import ProfileHomeView, ProfilePasswordChangeView, ProfileDeleteView, \
    ProfileScheduleListView, ProfileBookmarkListView, UpdownListView, ProfileScheduleUpdownScoreView, \
    ProfileReviewUpdownScoreView

urlpatterns = [
    url(r'^$', ProfileHomeView.as_view(), name='home'),
    url(r'^password-change/$', ProfilePasswordChangeView.as_view(), name='password_change'),
    url(r'^delete/$', ProfileDeleteView.as_view(), name='delete'),
    url(r'^schedule-list/$', ProfileScheduleListView.as_view(), name='schedule_list'),
    url(r'^bookmark-list/$', ProfileBookmarkListView.as_view(), name='bookmark_list'),
    url(r'^updown-list/$', UpdownListView.as_view(), name='updown_list'),
    url(r'^schedule-list/(?P<schedule_id>\d+)/updown$', ProfileScheduleUpdownScoreView.as_view(), name='schedule_updown'),
    url(r'^review-list/(?P<review_id>\d+)/updown$', ProfileReviewUpdownScoreView.as_view(), name='review_updown'),
]
