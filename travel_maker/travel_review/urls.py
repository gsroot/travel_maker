from django.conf.urls import url

from travel_maker.travel_review.views import TravelReviewCreateView, TravelReviewDeleteView

urlpatterns = [
    url(r'^create/(?P<travel_info>\d+)/$', TravelReviewCreateView.as_view(), name='create'),
    url(r'^delete/(?P<pk>\d+)/$', TravelReviewDeleteView.as_view(), name='delete'),
]
