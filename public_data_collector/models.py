from django.db import models


class Area(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=20)


class Sigungu(models.Model):
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    code = models.IntegerField()
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = ('area', 'code',)


class SmallArea(models.Model):
    sigungu = models.ForeignKey(Sigungu, on_delete=models.CASCADE)
    code = models.IntegerField()
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = ('sigungu', 'code',)


class Progress(models.Model):
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
    last_progress_date = models.DateTimeField(auto_now=True)
    fully_completed_area_count = models.IntegerField(default=0)
    percent = models.IntegerField(default=0)
