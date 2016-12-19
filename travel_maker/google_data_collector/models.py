from django.db import models

from django.db.models import ForeignKey, CharField, PositiveSmallIntegerField, OneToOneField, PositiveIntegerField

from travel_maker.public_data_collector.models import TravelInfo


class GooglePlaceInfo(models.Model):
    place_id = CharField(max_length=100)
    travel_info = OneToOneField(TravelInfo, on_delete=models.PROTECT)

    class Meta:
        ordering = ['id']


class GooglePlaceReviewInfo(models.Model):
    place_info = ForeignKey(GooglePlaceInfo, on_delete=models.PROTECT)
    author_name = CharField(max_length=200)
    profile_photo_url = CharField(max_length=500, blank=True)
    rating = PositiveSmallIntegerField()
    text = CharField(max_length=2000)
    time = models.DateTimeField()


class Progress(models.Model):
    last_progress_date = models.DateTimeField(auto_now=True)
    percent = models.IntegerField(default=0)

    class Meta:
        abstract = True


class GoogleApiProgress(Progress):
    TOTAL_ITEM_CNT = 0

    collector_type = models.CharField(max_length=100)
    travel_info = models.OneToOneField(TravelInfo, null=True, on_delete=models.PROTECT)
    place_info = models.OneToOneField(GooglePlaceInfo, null=True, on_delete=models.PROTECT)
    item_complete_count = models.IntegerField(default=0)

    @classmethod
    def set_total_item_count(cls, cnt):
        cls.TOTAL_ITEM_CNT = cnt
