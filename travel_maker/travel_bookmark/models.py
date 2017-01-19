from django.db import models
from django.db.models import ForeignKey, DateTimeField
from django.urls import reverse

from travel_maker.account.models import TmUser
from travel_maker.public_data_collector.models import TravelInfo
from travel_maker.travel_schedule.models import TravelSchedule


class TravelBookmark(models.Model):
    owner = ForeignKey(TmUser, on_delete=models.CASCADE)
    travel_info = ForeignKey(TravelInfo, on_delete=models.CASCADE)
    created = DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('travel_info:detail', args=(self.travel_info.id,))


class ScheduleBookmark(models.Model):
    owner = ForeignKey(TmUser, on_delete=models.CASCADE)
    travel_schedule = ForeignKey(TravelSchedule, on_delete=models.CASCADE)
    created = DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('travel_schedule:detail', args=(self.travel_schedule.id,))
