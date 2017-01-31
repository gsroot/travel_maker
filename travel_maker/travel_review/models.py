from bs4 import BeautifulSoup
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from updown.models import Vote

from travel_maker.account.models import TmUser
from travel_maker.models import Votable, TimeStamped
from travel_maker.public_data_collector.models import TravelInfo


class TravelReview(TimeStamped, Votable):
    travel_info = models.ForeignKey(TravelInfo, on_delete=models.CASCADE)
    owner = models.ForeignKey(TmUser, on_delete=models.CASCADE)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)])
    content = models.CharField(max_length=5000, validators=[
        RegexValidator(regex='^.{10,}$', message='최소 10글자 이상 입력해 주세요', code='tooshort')])
    tags = TaggableManager(
        blank=True,
        help_text=_('각 태그는 쉼표(,)로 구분됩니다')
    )

    @property
    def text(self):
        soup = BeautifulSoup(self.content, 'html.parser')
        [s.extract() for s in soup('img')]
        text = " ".join(soup.strings)
        text = text[:100] + '..' if len(text) > 100 else text
        return text

    def get_absolute_url(self):
        return reverse('travel_review:detail', args=(self.id,))

    def clean(self):
        if not self.rating:
            raise ValidationError('평점을 선택해 주셔야 합니다')
        if int(self.rating % 0.5) != 0:
            raise ValidationError('평점에 적절하지 않은 값이 입력되었습니다')
