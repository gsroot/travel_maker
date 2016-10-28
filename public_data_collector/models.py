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
    addr1 = models.CharField(max_length=100, null=True, blank=True)
    addr2 = models.CharField(max_length=100, null=True, blank=True)
    area_code = models.IntegerField(null=True)
    sigungu_code = models.IntegerField(null=True)
    sigungu = models.ForeignKey(Sigungu, on_delete=models.SET_NULL, null=True)
    contenttype = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    cat1_code = models.CharField(max_length=20)
    cat2_code = models.CharField(max_length=20)
    cat3_code = models.CharField(max_length=20)
    cat3 = models.ForeignKey(Category3, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=100)
    image = models.CharField(max_length=200, null=True, blank=True)
    thumbnail = models.CharField(max_length=200, null=True, blank=True)
    mapx = models.FloatField(null=True)
    mapy = models.FloatField(null=True)
    mlevel = models.IntegerField(null=True)
    is_booktour = models.BooleanField(default=False)
    tel = models.CharField(max_length=200, null=True, blank=True)
    readcount = models.IntegerField(null=True)
    created = models.DateTimeField(null=True, blank=True)
    modified = models.DateTimeField(null=True, blank=True)


class TravelOverviewInfo(models.Model):
    travel_info = models.OneToOneField(TravelInfo, on_delete=models.PROTECT, primary_key=True)
    telname = models.CharField(max_length=50, null=True, blank=True)
    homepage = models.CharField(max_length=1000, null=True, blank=True)
    overview = models.CharField(max_length=10000, null=True, blank=True)


class TravelIntroInfo(models.Model):
    travel_info = models.OneToOneField(TravelInfo, on_delete=models.PROTECT, primary_key=True)

    class Meta:
        abstract = True


class TourspotIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, null=True, blank=True)
    chkbabycarriage = models.CharField(max_length=50, null=True, blank=True)
    chkcreditcard = models.CharField(max_length=50, null=True, blank=True)
    chkpet = models.CharField(max_length=50, null=True, blank=True)
    expagerange = models.CharField(max_length=200, null=True, blank=True)
    expguide = models.CharField(max_length=10000, null=True, blank=True)
    heritage1 = models.BooleanField(default=False)
    heritage2 = models.BooleanField(default=False)
    heritage3 = models.BooleanField(default=False)
    infocenter = models.CharField(max_length=500, null=True, blank=True)
    opendate = models.CharField(max_length=500, null=True, blank=True)
    parking = models.CharField(max_length=1000, null=True, blank=True)
    restdate = models.CharField(max_length=500, null=True, blank=True)
    useseason = models.CharField(max_length=500, null=True, blank=True)
    usetime = models.CharField(max_length=500, null=True, blank=True)


class CulturalFacilityIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, null=True, blank=True)
    chkbabycarriage = models.CharField(max_length=50, null=True, blank=True)
    chkcreditcard = models.CharField(max_length=50, null=True, blank=True)
    chkpet = models.CharField(max_length=50, null=True, blank=True)
    discountinfo = models.CharField(max_length=1000, null=True, blank=True)
    infocenter = models.CharField(max_length=500, null=True, blank=True)
    parking = models.CharField(max_length=1000, null=True, blank=True)
    parkingfee = models.CharField(max_length=500, null=True, blank=True)
    restdate = models.CharField(max_length=500, null=True, blank=True)
    usefee = models.CharField(max_length=500, null=True, blank=True)
    usetime = models.CharField(max_length=500, null=True, blank=True)
    scale = models.CharField(max_length=200, null=True, blank=True)
    spendtime = models.CharField(max_length=500, null=True, blank=True)


class FestivalIntroInfo(TravelIntroInfo):
    agelimit = models.CharField(max_length=100, null=True, blank=True)
    bookingplace = models.CharField(max_length=500, null=True, blank=True)
    discountinfo = models.CharField(max_length=500, null=True, blank=True)
    eventenddate = models.DateField(null=True, blank=True)
    eventhomepage = models.CharField(max_length=1000, null=True, blank=True)
    eventplace = models.CharField(max_length=200, null=True, blank=True)
    eventstartdate = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=100, null=True, blank=True)
    placeinfo = models.CharField(max_length=1000, null=True, blank=True)
    playtime = models.CharField(max_length=500, null=True, blank=True)
    program = models.CharField(max_length=2000, null=True, blank=True)
    spendtime = models.CharField(max_length=500, null=True, blank=True)
    sponsor1 = models.CharField(max_length=100, null=True, blank=True)
    sponsor1tel = models.CharField(max_length=200, null=True, blank=True)
    sponsor2 = models.CharField(max_length=100, null=True, blank=True)
    sponsor2tel = models.CharField(max_length=200, null=True, blank=True)
    subevent = models.CharField(max_length=2000, null=True, blank=True)
    usefee = models.CharField(max_length=500, null=True, blank=True)


class TourCourseIntroInfo(TravelIntroInfo):
    distance = models.CharField(max_length=500, null=True, blank=True)
    infocenter = models.CharField(max_length=500, null=True, blank=True)
    schedule = models.CharField(max_length=500, null=True, blank=True)
    taketime = models.CharField(max_length=500, null=True, blank=True)
    theme = models.CharField(max_length=500, null=True, blank=True)


class LeportsIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, null=True, blank=True)
    chkbabycarriage = models.CharField(max_length=50, null=True, blank=True)
    chkcreditcard = models.CharField(max_length=50, null=True, blank=True)
    chkpet = models.CharField(max_length=50, null=True, blank=True)
    expagerange = models.CharField(max_length=200, null=True, blank=True)
    infocenter = models.CharField(max_length=500, null=True, blank=True)
    openperiod = models.CharField(max_length=500, null=True, blank=True)
    parkingfee = models.CharField(max_length=500, null=True, blank=True)
    parking = models.CharField(max_length=1000, null=True, blank=True)
    reservation = models.CharField(max_length=500, null=True, blank=True)
    restdate = models.CharField(max_length=500, null=True, blank=True)
    scale = models.CharField(max_length=200, null=True, blank=True)
    usefee = models.CharField(max_length=500, null=True, blank=True)
    usetime = models.CharField(max_length=500, null=True, blank=True)


class LodgingIntroInfo(TravelIntroInfo):
    accomcount = models.CharField(max_length=200, null=True, blank=True)
    benikia = models.BooleanField(default=False)
    checkintime = models.CharField(max_length=200, null=True, blank=True)
    checkouttime = models.CharField(max_length=200, null=True, blank=True)
    chkcooking = models.CharField(max_length=200, null=True, blank=True)
    foodplace = models.CharField(max_length=500, null=True, blank=True)
    goodstay = models.BooleanField(default=False)
    hanok = models.BooleanField(default=False)
    infocenter = models.CharField(max_length=500, null=True, blank=True)
    parking = models.CharField(max_length=1000, null=True, blank=True)
    pickup = models.CharField(max_length=500, null=True, blank=True)
    roomcount = models.CharField(max_length=200, null=True, blank=True)
    reservation = models.CharField(max_length=500, null=True, blank=True)
    reservationurl = models.CharField(max_length=500, null=True, blank=True)
    roomtype = models.CharField(max_length=1000, null=True, blank=True)
    scale = models.CharField(max_length=200, null=True, blank=True)
    subfacility = models.CharField(max_length=1000, null=True, blank=True)
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
    chkbabycarriage = models.CharField(max_length=50, null=True, blank=True)
    chkcreditcard = models.CharField(max_length=50, null=True, blank=True)
    chkpet = models.CharField(max_length=50, null=True, blank=True)
    fairday = models.CharField(max_length=200, null=True, blank=True)
    infocenter = models.CharField(max_length=500, null=True, blank=True)
    opendate = models.CharField(max_length=500, null=True, blank=True)
    opentime = models.CharField(max_length=500, null=True, blank=True)
    parking = models.CharField(max_length=1000, null=True, blank=True)
    restdate = models.CharField(max_length=500, null=True, blank=True)
    restroom = models.CharField(max_length=500, null=True, blank=True)
    saleitem = models.CharField(max_length=500, null=True, blank=True)
    saleitemcost = models.CharField(max_length=500, null=True, blank=True)
    scale = models.CharField(max_length=200, null=True, blank=True)
    shopguide = models.CharField(max_length=2000, null=True, blank=True)


class RestaurantIntroInfo(TravelIntroInfo):
    chkcreditcard = models.CharField(max_length=50, null=True, blank=True)
    discountinfo = models.CharField(max_length=500, null=True, blank=True)
    firstmenu = models.CharField(max_length=200, null=True, blank=True)
    infocenter = models.CharField(max_length=500, null=True, blank=True)
    kidsfacility = models.BooleanField(default=False)
    opendate = models.CharField(max_length=500, null=True, blank=True)
    opentime = models.CharField(max_length=500, null=True, blank=True)
    packing = models.CharField(max_length=200, null=True, blank=True)
    parking = models.CharField(max_length=500, null=True, blank=True)
    reservation = models.CharField(max_length=500, null=True, blank=True)
    restdate = models.CharField(max_length=500, null=True, blank=True)
    scale = models.CharField(max_length=500, null=True, blank=True)
    seat = models.CharField(max_length=500, null=True, blank=True)
    smoking = models.CharField(max_length=50, null=True, blank=True)
    treatmenu = models.CharField(max_length=1000, null=True, blank=True)


class TravelDetailInfo(models.Model):
    travel_info = models.ForeignKey(TravelInfo, on_delete=models.PROTECT)

    class Meta:
        abstract = True


class DefaultTravelDetailInfo(TravelDetailInfo):
    serialnum = models.IntegerField()
    infoname = models.CharField(max_length=50, null=True, blank=True)
    infotext = models.CharField(max_length=10000, null=True, blank=True)

    class Meta:
        unique_together = ('travel_info', 'serialnum')


class TourCourseDetailInfo(TravelDetailInfo):
    sub_travel_info = models.OneToOneField(
        TravelInfo, on_delete=models.PROTECT, unique=True, null=True, blank=True, related_name='detailinfo'
    )
    subnum = models.IntegerField()
    subdetailalt = models.CharField(max_length=500, null=True, blank=True)
    subdetailimg = models.CharField(max_length=500, null=True, blank=True)
    subdetailoverview = models.CharField(max_length=5000, null=True, blank=True)
    subname = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = ('travel_info', 'subnum')


class LodgingDetailInfo(TravelDetailInfo):
    roomtitle = models.CharField(max_length=200, null=True, blank=True)
    roomsize1 = models.IntegerField(null=True)
    roomcount = models.IntegerField(null=True)
    roombasecount = models.IntegerField(null=True)
    roommaxcount = models.IntegerField(null=True)
    roomoffseasonminfee1 = models.IntegerField(null=True)
    roomoffseasonminfee2 = models.IntegerField(null=True)
    roompeakseasonminfee1 = models.IntegerField(null=True)
    roompeakseasonminfee2 = models.IntegerField(null=True)
    roomintro = models.CharField(max_length=1000, null=True, blank=True)
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
    roomTable = models.NullBooleanField(null=True)
    roomhairdryer = models.NullBooleanField(null=True)
    roomsize2 = models.IntegerField(null=True)
    roomimg1 = models.CharField(max_length=500, null=True, blank=True)
    roomimg1alt = models.CharField(max_length=500, null=True, blank=True)
    roomimg2 = models.CharField(max_length=500, null=True, blank=True)
    roomimg2alt = models.CharField(max_length=500, null=True, blank=True)
    roomimg3 = models.CharField(max_length=500, null=True, blank=True)
    roomimg3alt = models.CharField(max_length=500, null=True, blank=True)
    roomimg4 = models.CharField(max_length=500, null=True, blank=True)
    roomimg4alt = models.CharField(max_length=500, null=True, blank=True)
    roomimg5 = models.CharField(max_length=500, null=True, blank=True)
    roomimg5alt = models.CharField(max_length=500, null=True, blank=True)


class TravelImageInfo(models.Model):
    travel_info = models.ForeignKey(TravelInfo, on_delete=models.PROTECT)
    serialnum = models.CharField(max_length=100, null=True, blank=True)
    originimgurl = models.CharField(max_length=500, null=True, blank=True)
    smallimageurl = models.CharField(max_length=500, null=True, blank=True)

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
    travel_info = models.OneToOneField(TravelInfo, null=True, on_delete=models.PROTECT)
    info_complete_count = models.IntegerField(default=0)
