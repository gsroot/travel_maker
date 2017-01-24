from django.db import models
from django.db.models import CharField, DateField, TextField, ForeignKey
from taggit.managers import TaggableManager

from travel_maker.public_data_collector.models import TravelInfo


class BlogData(models.Model):
    travel_info = ForeignKey(TravelInfo)
    bloggerlink = CharField(max_length=200)
    bloggername = CharField(max_length=200)
    title = CharField(max_length=200)
    description = CharField(max_length=1000)
    link = CharField(max_length=200)
    postdate = DateField(null=True, blank=True)
    text = TextField()
    tags = TaggableManager()

    class Meta:
        unique_together = ('travel_info', 'link')


class Progress(models.Model):
    last_progress_date = models.DateTimeField(auto_now=True)
    percent = models.IntegerField(default=0)

    class Meta:
        abstract = True


class BlogDataProgress(Progress):
    collector_type = models.CharField(max_length=100)
    travel_info = models.OneToOneField(TravelInfo, null=True, on_delete=models.SET_NULL)
    target_info_count = models.IntegerField(default=0)
    info_complete_count = models.IntegerField(default=0)
