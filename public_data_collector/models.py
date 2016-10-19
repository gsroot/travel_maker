from datetime import datetime

from django.db import models
from django.utils import timezone


class District(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=20)

    class Meta:
        abstract = True


class Area(District):
    code = models.IntegerField(unique=True)


class Sigungu(District):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('area', 'code')


class SmallArea(District):
    sigungu = models.ForeignKey(Sigungu, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('sigungu', 'code')


class Category(models.Model):
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Category1(Category):
    pass


class Category2(Category):
    cat1 = models.ForeignKey(Category1, on_delete=models.CASCADE)


class Category3(Category):
    cat2 = models.ForeignKey(Category2, on_delete=models.CASCADE)


class Progress(models.Model):
    last_progress_date = models.DateTimeField(auto_now=True)
    percent = models.IntegerField(default=0)

    class Meta:
        abstract = True


class AreaCodeProgress(Progress):
    NO = 0
    AR = 1
    SG = 2
    SM = 3
    LEVELS = (
        (NO, 'None'),
        (AR, 'Area'),
        (SG, 'Sigungu'),
        (SM, 'Smallarea')
    )
    TOTAL_AREA_CNT = 17

    level = models.IntegerField(choices=LEVELS, default=NO)
    area = models.OneToOneField(Area, null=True)
    sigungu = models.OneToOneField(Sigungu, null=True)
    area_complete_count = models.IntegerField(default=0)


class CategoryCodeProgress(Progress):
    NO = 0
    C1 = 1
    C2 = 2
    C3 = 3
    LEVELS = (
        (NO, 'None'),
        (C1, 'Category1'),
        (C2, 'Category2'),
        (C3, 'Category3')
    )
    TOTAL_CATEGORY_CNT = 7

    level = models.IntegerField(choices=LEVELS, default=NO)
    cat1 = models.OneToOneField(Category1, null=True)
    cat2 = models.OneToOneField(Category2, null=True)
    cat1_complete_count = models.IntegerField(default=0)

