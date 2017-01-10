from django.conf.urls import url

from travel_maker.account.views import ProfileHomeView, ProfilePasswordChangeView, ProfileDeleteView

urlpatterns = [
    url(r'^$', ProfileHomeView.as_view(), name='home'),
    url(r'^password-change/$', ProfilePasswordChangeView.as_view(), name='password_change'),
    url(r'^delete/$', ProfileDeleteView.as_view(), name='delete'),
]
