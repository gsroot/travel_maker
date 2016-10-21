from django.db import models


class District(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=20)

    class Meta:
        abstract = True


class Area(District):
    code = models.IntegerField(unique=True)


class Sigungu(District):
    area = models.ForeignKey(Area, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('area', 'code')


class SmallArea(District):
    sigungu = models.ForeignKey(Sigungu, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('sigungu', 'code')


class ContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)


class Category(models.Model):
    code = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=100)

    class Meta:
        abstract = True


class Category1(Category):
    pass


class Category2(Category):
    cat1 = models.ForeignKey(Category1, on_delete=models.PROTECT)


class Category3(Category):
    cat2 = models.ForeignKey(Category2, on_delete=models.PROTECT)


class TravelInfo(models.Model):
    addr1 = models.CharField(max_length=100)
    addr2 = models.CharField(max_length=100, null=True, blank=True)
    area_code = models.IntegerField()
    sigungu_code = models.IntegerField()
    sigungu = models.ForeignKey(Sigungu, on_delete=models.PROTECT)
    contenttype = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    cat1_code = models.CharField(max_length=20)
    cat2_code = models.CharField(max_length=20)
    cat3_code = models.CharField(max_length=20)
    cat3 = models.ForeignKey(Category3, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    image = models.CharField(max_length=200, null=True, blank=True)
    thumbnail = models.CharField(max_length=200, null=True, blank=True)
    mapx = models.FloatField()
    mapy = models.FloatField()
    mlevel = models.IntegerField()
    is_book_tour = models.BooleanField()
    tel = models.CharField(max_length=20, null=True, blank=True)
    readcount = models.IntegerField()
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)


class AdditionalInfo(models.Model):
    travel_info = models.OneToOneField(TravelInfo, on_delete=models.PROTECT, null=True)

    class Meta:
        abstract = True


class OverviewInfo(AdditionalInfo):
    telname = models.CharField(max_length=50, null=True, blank=True)
    homepage = models.CharField(max_length=200, null=True, blank=True)
    overview = models.CharField(max_length=5000, null=True, blank=True)


class TourspotIntroInfo(AdditionalInfo):
    accomcount = models.CharField(max_length=50, null=True, blank=True)
    chkbabycarriage = models.CharField(max_length=20, null=True, blank=True)
    chkcreditcard = models.CharField(max_length=20, null=True, blank=True)
    chkpet = models.CharField(max_length=20, null=True, blank=True)
    expagerange = models.CharField(max_length=50, null=True, blank=True)
    expguide = models.CharField(max_length=1000, null=True, blank=True)
    heritage1 = models.BooleanField(default=False)
    heritage2 = models.BooleanField(default=False)
    heritage3 = models.BooleanField(default=False)
    infocenter = models.CharField(max_length=200, null=True, blank=True)
    opendate = models.CharField(max_length=200, null=True, blank=True)
    parking = models.CharField(max_length=500, null=True, blank=True)
    restdate = models.CharField(max_length=200, null=True, blank=True)
    useseason = models.CharField(max_length=200, null=True, blank=True)
    usetime = models.CharField(max_length=200, null=True, blank=True)


class CulturalFacilityIntroInfo(AdditionalInfo):
    accomcount = models.CharField(max_length=50, null=True, blank=True)
    chkbabycarriage = models.CharField(max_length=20, null=True, blank=True)
    chkcreditcard = models.CharField(max_length=20, null=True, blank=True)
    chkpet = models.CharField(max_length=20, null=True, blank=True)
    discountinfo = models.CharField(max_length=500, null=True, blank=True)
    infocenter = models.CharField(max_length=200, null=True, blank=True)
    parking = models.CharField(max_length=500, null=True, blank=True)
    parkingfee = models.CharField(max_length=500, null=True, blank=True)
    restdate = models.CharField(max_length=200, null=True, blank=True)
    usefee = models.CharField(max_length=200, null=True, blank=True)
    usetime = models.CharField(max_length=200, null=True, blank=True)
    scale = models.CharField(max_length=100, null=True, blank=True)
    spendtime = models.CharField(max_length=200, null=True, blank=True)


class DefaultDetailInfo(AdditionalInfo):
    infoname = models.CharField(max_length=50, null=True, blank=True)
    infotext = models.CharField(max_length=2000, null=True, blank=True)


class ImageInfo(AdditionalInfo):
    originimgurl = models.CharField(max_length=200, null=True, blank=True)
    smallimageurl = models.CharField(max_length=200, null=True, blank=True)


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
    area = models.OneToOneField(Area, null=True, on_delete=models.PROTECT)
    sigungu = models.OneToOneField(Sigungu, null=True, on_delete=models.PROTECT)
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
    cat1 = models.OneToOneField(Category1, null=True, on_delete=models.PROTECT)
    cat2 = models.OneToOneField(Category2, null=True, on_delete=models.PROTECT)
    cat1_complete_count = models.IntegerField(default=0)
