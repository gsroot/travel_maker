from django.conf.urls import url

from travel_maker.account.views import ProfileHomeView

urlpatterns = [
    url(r'^$', ProfileHomeView.as_view(), name='home'),
]