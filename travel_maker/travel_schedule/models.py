from django.db import models
from django.db.models import ForeignKey, CharField, TextField, DateTimeField, PositiveSmallIntegerField
from django.db.models import OneToOneField
from schedule.models import Event
from taggit.managers import TaggableManager

from travel_maker.public_data_collector.models import TravelInfo


class TravelSchedule(models.Model):
    title = CharField(max_length=200)
    description = TextField(max_length=5000)
    start = DateTimeField()
    end = DateTimeField()
    people_count = PositiveSmallIntegerField(default=1)
    tags = TaggableManager()


class TravelScheduleEvent(models.Model):
    event = OneToOneField(Event, null=True, on_delete=models.SET_NULL)
    travel_schedule = ForeignKey(TravelSchedule, null=True, on_delete=models.SET_NULL)

    class Meta:
        abstract = True


class TravelInfoScheduleEvent(TravelScheduleEvent):
    travel_info = OneToOneField(TravelInfo, on_delete=models.PROTECT)
