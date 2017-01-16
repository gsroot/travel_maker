from collections import Counter
from statistics import mean

from django.db import models
from django.urls import reverse


class District(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=20)

    class Meta:
        abstract = True


class Area(District):
    code = models.IntegerField(unique=True)

    def __str__(self):
        return self.name

    @property
    def info(self):
        title = self.name

        area_selector = {
            '경기도': '경기 수원시',
            '강원도': '강원 원주시',
            '충청북도': '청주시',
            '충청남도': '충남 홍성군',
            '경상북도': '안동시',
            '경상남도': '창원시',
            '전라북도': '전주시',
            '전라남도': '전남 무안군',
            '제주도': '제주특별자치도',
        }
        if title == '서울':
            title = '서울특별시'
        elif title in ['인천', '대전', '대구', '광주', '부산', '울산']:
            title += '광역시'
        elif title in area_selector:
            title = area_selector[title]

        return TravelInfo.objects.get(title=title)


class Sigungu(District):
    area = models.ForeignKey(Area, on_delete=models.PROTECT)

    def __str__(self):
        return ' '.join([self.area.name, self.name])

    class Meta:
        unique_together = ('area', 'code')


class SmallArea(District):
    sigungu = models.ForeignKey(Sigungu, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('sigungu', 'code')


class ContentType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


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
    addr1 = models.CharField(max_length=100, blank=True, default='')
    addr2 = models.CharField(max_length=100, blank=True, default='')
    area_code = models.IntegerField(null=True)
    sigungu_code = models.IntegerField(null=True)
    sigungu = models.ForeignKey(Sigungu, on_delete=models.SET_NULL, null=True)
    contenttype = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    cat1_code = models.CharField(max_length=20)
    cat2_code = models.CharField(max_length=20)
    cat3_code = models.CharField(max_length=20)
    cat3 = models.ForeignKey(Category3, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    image = models.CharField(max_length=200, blank=True, default='')
    thumbnail = models.CharField(max_length=200, blank=True, default='')
    mapx = models.FloatField(null=True)
    mapy = models.FloatField(null=True)
    mlevel = models.IntegerField(null=True)
    is_booktour = models.BooleanField(default=False)
    tel = models.CharField(max_length=200, blank=True, default='')
    readcount = models.IntegerField(null=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title

    @property
    def map_x(self):
        if self.contenttype.name == '여행코스':
            map_x_list = [info.sub_travel_info.mapx for info in self.tourcoursedetailinfo_set.all()
                     if info.sub_travel_info and info.sub_travel_info.mapx]
            return mean(map_x_list)
        else:
            return self.mapx

    @property
    def map_y(self):
        if self.contenttype.name == '여행코스':
            map_y_list = [info.sub_travel_info.mapy for info in self.tourcoursedetailinfo_set.all()
                     if info.sub_travel_info and info.sub_travel_info.mapy]
            return mean(map_y_list)
        else:
            return self.mapy

    @property
    def reviews_cnt(self):
        googlereview_cnt = self.googleplaceinfo.googleplacereviewinfo_set.count() \
            if hasattr(self, 'googleplaceinfo') else 0
        travelreview_cnt = self.travelreview_set.count()
        return googlereview_cnt + travelreview_cnt

    @property
    def rating(self):
        if (hasattr(self, 'googleplaceinfo') and self.googleplaceinfo.googleplacereviewinfo_set.all()) \
                or self.travelreview_set.all():
            google_ratings = [
                review.rating for review in self.googleplaceinfo.googleplacereviewinfo_set.all()
                ] if hasattr(self, 'googleplaceinfo') else []
            travel_ratings = [review.rating for review in self.travelreview_set.all()]
            return round(mean(google_ratings + travel_ratings), 2)
        else:
            return None

    @property
    def blogs(self):
        return self.blogdata_set.all()

    @property
    def primary_blogs(self):
        return self.blogdata_set.all()[:10]

    @property
    def tags(self):
        return [tag for data in self.blogdata_set.all() for tag in data.tags.all()]

    @property
    def primary_three_tags(self):
        return sorted(Counter(self.tags).items(), key=lambda pair: pair[1], reverse=True)[:3]

    @property
    def primary_six_tags(self):
        return sorted(Counter(self.tags).items(), key=lambda pair: pair[1], reverse=True)[:6]

    def get_absolute_url(self):
        return reverse('travel_info:detail', args=(self.id,))


class TravelOverviewInfo(models.Model):
    travel_info = models.OneToOneField(TravelInfo, on_delete=models.PROTECT, primary_key=True)
    telname = models.CharField(max_length=50, blank=True, default='')
    homepage = models.CharField(max_length=1000, blank=True, default='')
    overview = models.CharField(max_length=10000, blank=True, default='')


class TravelIntroInfo(models.Model):
    travel_info = models.OneToOneField(TravelInfo, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        abstract = True


class TourspotIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, blank=True, default='')
    chkbabycarriage = models.CharField(max_length=50, blank=True, default='')
    chkcreditcard = models.CharField(max_length=50, blank=True, default='')
    chkpet = models.CharField(max_length=50, blank=True, default='')
    expagerange = models.CharField(max_length=200, blank=True, default='')
    expguide = models.CharField(max_length=10000, blank=True, default='')
    heritage1 = models.BooleanField(default=False)
    heritage2 = models.BooleanField(default=False)
    heritage3 = models.BooleanField(default=False)
    infocenter = models.CharField(max_length=500, blank=True, default='')
    opendate = models.CharField(max_length=500, blank=True, default='')
    parking = models.CharField(max_length=1000, blank=True, default='')
    restdate = models.CharField(max_length=500, blank=True, default='')
    useseason = models.CharField(max_length=500, blank=True, default='')
    usetime = models.CharField(max_length=500, blank=True, default='')


class CulturalFacilityIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, blank=True, default='')
    chkbabycarriage = models.CharField(max_length=50, blank=True, default='')
    chkcreditcard = models.CharField(max_length=50, blank=True, default='')
    chkpet = models.CharField(max_length=50, blank=True, default='')
    discountinfo = models.CharField(max_length=1000, blank=True, default='')
    infocenter = models.CharField(max_length=500, blank=True, default='')
    parking = models.CharField(max_length=1000, blank=True, default='')
    parkingfee = models.CharField(max_length=500, blank=True, default='')
    restdate = models.CharField(max_length=500, blank=True, default='')
    usefee = models.CharField(max_length=500, blank=True, default='')
    usetime = models.CharField(max_length=500, blank=True, default='')
    scale = models.CharField(max_length=200, blank=True, default='')
    spendtime = models.CharField(max_length=500, blank=True, default='')


class FestivalIntroInfo(TravelIntroInfo):
    agelimit = models.CharField(max_length=100, blank=True, default='')
    bookingplace = models.CharField(max_length=500, blank=True, default='')
    discountinfo = models.CharField(max_length=500, blank=True, default='')
    eventenddate = models.DateField(null=True, blank=True)
    eventhomepage = models.CharField(max_length=1000, blank=True, default='')
    eventplace = models.CharField(max_length=200, blank=True, default='')
    eventstartdate = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=100, blank=True, default='')
    placeinfo = models.CharField(max_length=1000, blank=True, default='')
    playtime = models.CharField(max_length=500, blank=True, default='')
    program = models.CharField(max_length=2000, blank=True, default='')
    spendtime = models.CharField(max_length=500, blank=True, default='')
    sponsor1 = models.CharField(max_length=100, blank=True, default='')
    sponsor1tel = models.CharField(max_length=200, blank=True, default='')
    sponsor2 = models.CharField(max_length=100, blank=True, default='')
    sponsor2tel = models.CharField(max_length=200, blank=True, default='')
    subevent = models.CharField(max_length=2000, blank=True, default='')
    usefee = models.CharField(max_length=500, blank=True, default='')


class TourCourseIntroInfo(TravelIntroInfo):
    distance = models.CharField(max_length=500, blank=True, default='')
    infocenter = models.CharField(max_length=500, blank=True, default='')
    schedule = models.CharField(max_length=500, blank=True, default='')
    taketime = models.CharField(max_length=500, blank=True, default='')
    theme = models.CharField(max_length=500, blank=True, default='')


class LeportsIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, blank=True, default='')
    chkbabycarriage = models.CharField(max_length=50, blank=True, default='')
    chkcreditcard = models.CharField(max_length=50, blank=True, default='')
    chkpet = models.CharField(max_length=50, blank=True, default='')
    expagerange = models.CharField(max_length=200, blank=True, default='')
    infocenter = models.CharField(max_length=500, blank=True, default='')
    openperiod = models.CharField(max_length=500, blank=True, default='')
    parkingfee = models.CharField(max_length=500, blank=True, default='')
    parking = models.CharField(max_length=1000, blank=True, default='')
    reservation = models.CharField(max_length=500, blank=True, default='')
    restdate = models.CharField(max_length=500, blank=True, default='')
    scale = models.CharField(max_length=200, blank=True, default='')
    usefee = models.CharField(max_length=500, blank=True, default='')
    usetime = models.CharField(max_length=500, blank=True, default='')


class LodgingIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, blank=True, default='')
    benikia = models.BooleanField(default=False)
    checkintime = models.CharField(max_length=200, blank=True, default='')
    checkouttime = models.CharField(max_length=200, blank=True, default='')
    chkcooking = models.CharField(max_length=200, blank=True, default='')
    foodplace = models.CharField(max_length=500, blank=True, default='')
    goodstay = models.BooleanField(default=False)
    hanok = models.BooleanField(default=False)
    infocenter = models.CharField(max_length=500, blank=True, default='')
    parking = models.CharField(max_length=1000, blank=True, default='')
    pickup = models.CharField(max_length=500, blank=True, default='')
    roomcount = models.CharField(max_length=200, blank=True, default='')
    reservation = models.CharField(max_length=500, blank=True, default='')
    reservationurl = models.CharField(max_length=500, blank=True, default='')
    roomtype = models.CharField(max_length=1000, blank=True, default='')
    scale = models.CharField(max_length=200, blank=True, default='')
    subfacility = models.CharField(max_length=1000, blank=True, default='')
    barbecue = models.NullBooleanField(null=True)
    beauty = models.NullBooleanField(null=True)
    beverage = models.NullBooleanField(null=True)
    bicycle = models.NullBooleanField(null=True)
    campfire = models.NullBooleanField(null=True)
    fitness = models.NullBooleanField(null=True)
    karaoke = models.NullBooleanField(null=True)
    publicbath = models.NullBooleanField(null=True)
    publicpc = models.NullBooleanField(null=True)
    sauna = models.NullBooleanField(null=True)
    seminar = models.NullBooleanField(null=True)
    sports = models.NullBooleanField(null=True)


class ShoppingIntroInfo(TravelIntroInfo):
    chkbabycarriage = models.CharField(max_length=50, blank=True, default='')
    chkcreditcard = models.CharField(max_length=50, blank=True, default='')
    chkpet = models.CharField(max_length=50, blank=True, default='')
    fairday = models.CharField(max_length=200, blank=True, default='')
    infocenter = models.CharField(max_length=500, blank=True, default='')
    opendate = models.CharField(max_length=500, blank=True, default='')
    opentime = models.CharField(max_length=500, blank=True, default='')
    parking = models.CharField(max_length=1000, blank=True, default='')
    restdate = models.CharField(max_length=500, blank=True, default='')
    restroom = models.CharField(max_length=500, blank=True, default='')
    saleitem = models.CharField(max_length=500, blank=True, default='')
    saleitemcost = models.CharField(max_length=500, blank=True, default='')
    scale = models.CharField(max_length=200, blank=True, default='')
    shopguide = models.CharField(max_length=2000, blank=True, default='')


class RestaurantIntroInfo(TravelIntroInfo):
    chkcreditcard = models.CharField(max_length=50, blank=True, default='')
    discountinfo = models.CharField(max_length=500, blank=True, default='')
    firstmenu = models.CharField(max_length=200, blank=True, default='')
    infocenter = models.CharField(max_length=500, blank=True, default='')
    kidsfacility = models.BooleanField(default=False)
    opendate = models.CharField(max_length=500, blank=True, default='')
    opentime = models.CharField(max_length=500, blank=True, default='')
    packing = models.CharField(max_length=200, blank=True, default='')
    parking = models.CharField(max_length=500, blank=True, default='')
    reservation = models.CharField(max_length=500, blank=True, default='')
    restdate = models.CharField(max_length=500, blank=True, default='')
    scale = models.CharField(max_length=500, blank=True, default='')
    seat = models.CharField(max_length=500, blank=True, default='')
    smoking = models.CharField(max_length=50, blank=True, default='')
    treatmenu = models.CharField(max_length=1000, blank=True, default='')


class TravelDetailInfo(models.Model):
    travel_info = models.ForeignKey(TravelInfo, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class DefaultTravelDetailInfo(TravelDetailInfo):
    serialnum = models.IntegerField()
    infoname = models.CharField(max_length=50, blank=True, default='')
    infotext = models.CharField(max_length=10000, blank=True, default='')

    class Meta:
        unique_together = ('travel_info', 'serialnum')


class TourCourseDetailInfo(TravelDetailInfo):
    sub_travel_info = models.ForeignKey(
        TravelInfo, on_delete=models.SET_NULL, null=True, related_name='detailinfo'
    )
    subnum = models.IntegerField()
    subdetailalt = models.CharField(max_length=500, blank=True, default='')
    subdetailimg = models.CharField(max_length=500, blank=True, default='')
    subdetailoverview = models.CharField(max_length=5000, blank=True, default='')
    subname = models.CharField(max_length=200, blank=True, default='')

    class Meta:
        unique_together = ('travel_info', 'subnum')


class LodgingDetailInfo(TravelDetailInfo):
    roomtitle = models.CharField(max_length=200, blank=True, default='')
    roomsize1 = models.IntegerField(null=True)
    roomcount = models.IntegerField(null=True)
    roombasecount = models.IntegerField(null=True)
    roommaxcount = models.IntegerField(null=True)
    roomoffseasonminfee1 = models.IntegerField(null=True)
    roomoffseasonminfee2 = models.IntegerField(null=True)
    roompeakseasonminfee1 = models.IntegerField(null=True)
    roompeakseasonminfee2 = models.IntegerField(null=True)
    roomintro = models.CharField(max_length=1000, blank=True, default='')
    roombathfacility = models.NullBooleanField(null=True)
    roombath = models.NullBooleanField(null=True)
    roomhometheater = models.NullBooleanField(null=True)
    roomaircondition = models.NullBooleanField(null=True)
    roomtv = models.NullBooleanField(null=True)
    roompc = models.NullBooleanField(null=True)
    roomcable = models.NullBooleanField(null=True)
    roominternet = models.NullBooleanField(null=True)
    roomrefrigerator = models.NullBooleanField(null=True)
    roomtoiletries = models.NullBooleanField(null=True)
    roomsofa = models.NullBooleanField(null=True)
    roomcook = models.NullBooleanField(null=True)
    roomtable = models.NullBooleanField(null=True)
    roomhairdryer = models.NullBooleanField(null=True)
    roomsize2 = models.IntegerField(null=True)
    roomimg1 = models.CharField(max_length=500, blank=True, default='')
    roomimg1alt = models.CharField(max_length=500, blank=True, default='')
    roomimg2 = models.CharField(max_length=500, blank=True, default='')
    roomimg2alt = models.CharField(max_length=500, blank=True, default='')
    roomimg3 = models.CharField(max_length=500, blank=True, default='')
    roomimg3alt = models.CharField(max_length=500, blank=True, default='')
    roomimg4 = models.CharField(max_length=500, blank=True, default='')
    roomimg4alt = models.CharField(max_length=500, blank=True, default='')
    roomimg5 = models.CharField(max_length=500, blank=True, default='')
    roomimg5alt = models.CharField(max_length=500, blank=True, default='')

    @property
    def images(self):
        images = [
            {'src': getattr(self, 'roomimg{}'.format(i))} for i in range(1, 6) if getattr(self, 'roomimg{}'.format(i))]
        return images


class TravelImageInfo(models.Model):
    travel_info = models.ForeignKey(TravelInfo, on_delete=models.PROTECT)
    serialnum = models.CharField(max_length=100, blank=True, default='')
    originimgurl = models.CharField(max_length=500, blank=True, default='')
    smallimageurl = models.CharField(max_length=500, blank=True, default='')

    class Meta:
        unique_together = ('travel_info', 'serialnum')


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
    DEPTH = (
        (NO, 'None'),
        (AR, 'Area'),
        (SG, 'Sigungu'),
        (SM, 'Smallarea')
    )
    TOTAL_AREA_CNT = 17

    depth = models.IntegerField(choices=DEPTH, default=NO)
    area = models.OneToOneField(Area, null=True, on_delete=models.PROTECT)
    sigungu = models.OneToOneField(Sigungu, null=True, on_delete=models.PROTECT)
    area_complete_count = models.IntegerField(default=0)


class CategoryCodeProgress(Progress):
    NO = 0
    C1 = 1
    C2 = 2
    C3 = 3
    DEPTH = (
        (NO, 'None'),
        (C1, 'Category1'),
        (C2, 'Category2'),
        (C3, 'Category3')
    )
    TOTAL_CATEGORY_CNT = 7

    depth = models.IntegerField(choices=DEPTH, default=NO)
    cat1 = models.OneToOneField(Category1, null=True, on_delete=models.PROTECT)
    cat2 = models.OneToOneField(Category2, null=True, on_delete=models.PROTECT)
    cat1_complete_count = models.IntegerField(default=0)


class AdditionalInfoProgress(Progress):
    TOTAL_TRAVEL_INFO_CNT = TravelInfo.objects.count()

    info_type = models.CharField(max_length=100)
    travel_info = models.ForeignKey(TravelInfo, null=True, on_delete=models.PROTECT)
    info_complete_count = models.IntegerField(default=0)
