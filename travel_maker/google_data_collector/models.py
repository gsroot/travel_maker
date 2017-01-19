from django.db import models

from travel_maker.models import Votable
from travel_maker.public_data_collector.models import TravelInfo


class GooglePlaceInfo(models.Model):
    place_id = models.CharField(max_length=100)
    travel_info = models.OneToOneField(TravelInfo, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']


class GooglePlaceReviewInfo(Votable):
    place_info = models.ForeignKey(GooglePlaceInfo, on_delete=models.CASCADE)
    author_name = models.CharField(max_length=200)
    profile_photo_url = models.CharField(max_length=500, blank=True)
    rating = models.PositiveSmallIntegerField()
    text = models.CharField(max_length=2000)
    time = models.DateTimeField()


class Progress(models.Model):
    last_progress_date = models.DateTimeField(auto_now=True)
    percent = models.IntegerField(default=0)

    class Meta:
        abstract = True


class GoogleApiProgress(Progress):
    TOTAL_ITEM_CNT = 0

    collector_type = models.CharField(max_length=100)
    travel_info = models.OneToOneField(TravelInfo, null=True, on_delete=models.SET_NULL)
    place_info = models.OneToOneField(GooglePlaceInfo, null=True, on_delete=models.SET_NULL)
    item_complete_count = models.IntegerField(default=0)

    @classmethod
    def set_total_item_count(cls, cnt):
        cls.TOTAL_ITEM_CNT = cnt
