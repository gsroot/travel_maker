from django.db import models

from travel_maker.public_data_collector.models import TravelInfo


class Progress(models.Model):
    last_progress_date = models.DateTimeField(auto_now=True)
    percent = models.IntegerField(default=0)

    class Meta:
        abstract = True


class DataAnalysisProgress(Progress):
    collector_type = models.CharField(max_length=100)
    travel_info = models.OneToOneField(TravelInfo, null=True, on_delete=models.SET_NULL)
    target_info_count = models.IntegerField(default=0)
    info_complete_count = models.IntegerField(default=0)
