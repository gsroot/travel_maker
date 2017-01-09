from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from travel_maker.account.models import TmUser
from travel_maker.public_data_collector.models import TravelInfo


class TravelReview(models.Model):
    travel_info = models.ForeignKey(TravelInfo, on_delete=models.PROTECT)
    owner = models.ForeignKey(TmUser, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    content = models.CharField(max_length=5000)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def clean(self):
        if not self.rating:
            raise ValidationError('평점을 선택해 주셔야 합니다')
        if int(self.rating % 0.5) != 0:
            raise ValidationError('평점에 적절하지 않은 값이 입력되었습니다')
