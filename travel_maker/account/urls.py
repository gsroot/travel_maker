from django.conf.urls import url

from travel_maker.account.views import ProfileHomeView, ProfileDeleteView

urlpatterns = [
    url(r'^$', ProfileHomeView.as_view(), name='home'),
    url(r'^delete/$', ProfileDeleteView.as_view(), name='delete'),
]
