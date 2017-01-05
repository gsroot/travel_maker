from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import ForeignKey, CharField, TextField, PositiveSmallIntegerField, DateField, BooleanField
from django.db.models import OneToOneField
from django.utils.translation import ugettext_lazy as _
from schedule.models import Calendar
from schedule.models import Event
from taggit.managers import TaggableManager

from travel_maker.account.models import TmUser
from travel_maker.public_data_collector.models import TravelInfo


class TravelSchedule(models.Model):
    owner = ForeignKey(TmUser, on_delete=models.CASCADE)
    calendar = OneToOneField(Calendar, on_delete=models.CASCADE, null=True)
    title = CharField(max_length=200, verbose_name=_('여행의 이름을 지어주세요'))
    description = TextField(max_length=5000, blank=True, verbose_name=_('여행에 대해 기록하고 싶은 세부 내용을 적어보세요'))
    start = DateField(verbose_name=_('여행 첫째날'))
    end = DateField(verbose_name=_('여행 마지막날'))
    people_count = PositiveSmallIntegerField(default=1, verbose_name=_('여행 인원'))
    tags = TaggableManager(
        blank=True,
        verbose_name=_('여행의 특징을 태그로 남겨보세요'),
        help_text=_('각 태그는 쉼표(,)로 구분됩니다')
    )
    is_public = BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('travel_schedule:detail', args=(self.id,))

    @property
    def events(self):
        return self.travelinfoevent_set.all()


class TravelEvent(models.Model):
    event = OneToOneField(Event, null=True, on_delete=models.CASCADE)
    travel_schedule = ForeignKey(TravelSchedule, null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TravelInfoEvent(TravelEvent):
    travel_info = ForeignKey(TravelInfo, on_delete=models.PROTECT)
