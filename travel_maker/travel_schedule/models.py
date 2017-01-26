from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import ForeignKey, CharField, TextField, PositiveSmallIntegerField, DateField, BooleanField
from django.db.models import OneToOneField
from django.utils.translation import ugettext_lazy as _
from schedule.models import Calendar
from schedule.models import Event
from taggit.managers import TaggableManager

from travel_maker.account.models import TmUser
from travel_maker.models import Votable
from travel_maker.public_data_collector.models import TravelInfo


class TravelSchedule(Votable):
    owner = ForeignKey(TmUser, on_delete=models.CASCADE)
    calendar = OneToOneField(Calendar, on_delete=models.CASCADE, null=True)
    title = CharField(max_length=200)
    description = TextField(max_length=5000, blank=True)
    start = DateField()
    end = DateField()
    people_count = PositiveSmallIntegerField(
        default=1, validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    tags = TaggableManager(blank=True)
    is_public = BooleanField(default=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return self.title

    @property
    def summary(self):
        summary = self.description[:50] + '..' if len(self.description) > 50 else self.description
        return summary

    @property
    def tags_str(self):
        return ', '.join([tag.name for tag in self.tags.all()])

    @property
    def events(self):
        return self.travelinfoevent_set.all()

    @property
    def spots(self):
        return [e.travel_info for e in self.travelinfoevent_set.all().order_by('event__start')]

    @property
    def duration_days(self):
        return (self.end - self.start).days + 1

    def get_absolute_url(self):
        return reverse('travel_schedule:detail', args=(self.id,))

    def clean(self):
        if self.start and self.end:
            if self.start > self.end:
                raise ValidationError(_('여행 첫째날이 여행 마지막 날보다 같거나 빨라야 합니다'))
            if (self.end - self.start).days >= 30:
                raise ValidationError(_('여행 기간은 최대 30일 까지 가능합니다'))


class TravelEvent(models.Model):
    event = OneToOneField(Event, null=True, on_delete=models.CASCADE)
    travel_schedule = ForeignKey(TravelSchedule, null=True, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TravelInfoEvent(TravelEvent):
    travel_info = ForeignKey(TravelInfo, on_delete=models.CASCADE)
