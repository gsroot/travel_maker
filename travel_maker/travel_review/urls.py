from django.conf.urls import url
from updown.views import AddRatingFromModel

from travel_maker.travel_review.views import TravelReviewCreateView, TravelReviewDeleteView, TravelReviewDetailView

urlpatterns = [
    url(r'^(?P<pk>\d+)/$', TravelReviewDetailView.as_view(), name='detail'),
    url(r"^(?P<object_id>\d+)/rate/(?P<score>[\d\-]+)$", AddRatingFromModel(), {
        'app_label': 'travel_review',
        'model': 'TravelReview',
        'field_name': 'updown',
    }, name="updown"),
    url(r'^create/(?P<travel_info>\d+)/$', TravelReviewCreateView.as_view(), name='create'),
    url(r'^delete/(?P<pk>\d+)/$', TravelReviewDeleteView.as_view(), name='delete'),
]
