from django.db import models
from django.db.models import ForeignKey, DateTimeField
from django.urls import reverse

from travel_maker.account.models import TmUser
from travel_maker.public_data_collector.models import TravelInfo


class TravelBookmark(models.Model):
    owner = ForeignKey(TmUser, on_delete=models.CASCADE)
    travel_info = ForeignKey(TravelInfo, on_delete=models.CASCADE)
    created = DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        return reverse('travel_info:detail', args=(self.travel_info.id,))
