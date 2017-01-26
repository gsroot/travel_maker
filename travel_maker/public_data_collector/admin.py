from django.contrib import admin

from travel_maker.public_data_collector.models import TravelOverviewInfo, TourspotIntroInfo, \
    CulturalFacilityIntroInfo, FestivalIntroInfo, TourCourseIntroInfo, LeportsIntroInfo, LodgingIntroInfo, \
    ShoppingIntroInfo, RestaurantIntroInfo, TourCourseDetailInfo, DefaultTravelDetailInfo, LodgingDetailInfo, \
    TravelImageInfo, AreaCodeProgress, CategoryCodeProgress, AdditionalInfoProgress


class TravelOverviewInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TravelOverviewInfo._meta.fields]
    search_fields = ('travel_info__title',)


class TourspotIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TourspotIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class CulturalFacilityIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CulturalFacilityIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class FestivalIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in FestivalIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class TourCourseIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TourCourseIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class LeportsIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in LeportsIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class LodgingIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in LodgingIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class ShoppingIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ShoppingIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class RestaurantIntroInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in RestaurantIntroInfo._meta.fields]
    search_fields = ('travel_info__title',)


class DefaultTravelDetailInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in DefaultTravelDetailInfo._meta.fields]
    search_fields = ('travel_info__title',)


class TourCourseDetailInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TourCourseDetailInfo._meta.fields]
    search_fields = ('travel_info__title',)


class LodgingDetailInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in LodgingDetailInfo._meta.fields]
    search_fields = ('travel_info__title',)


class TravelImageInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TravelImageInfo._meta.fields]
    search_fields = ('travel_info__title',)


class AreaCodeProgressAdmin(admin.ModelAdmin):
    list_display = [f.name for f in AreaCodeProgress._meta.fields]


class CategoryCodeProgressAdmin(admin.ModelAdmin):
    list_display = [f.name for f in CategoryCodeProgress._meta.fields]


class AdditionalInfoProgressAdmin(admin.ModelAdmin):
    list_display = [f.name for f in AdditionalInfoProgress._meta.fields]


admin.site.register(TravelOverviewInfo, TravelOverviewInfoAdmin)
admin.site.register(TourspotIntroInfo, TourspotIntroInfoAdmin)
admin.site.register(CulturalFacilityIntroInfo, CulturalFacilityIntroInfoAdmin)
admin.site.register(FestivalIntroInfo, FestivalIntroInfoAdmin)
admin.site.register(TourCourseIntroInfo, TourCourseIntroInfoAdmin)
admin.site.register(LeportsIntroInfo, LeportsIntroInfoAdmin)
admin.site.register(LodgingIntroInfo, LodgingIntroInfoAdmin)
admin.site.register(ShoppingIntroInfo, ShoppingIntroInfoAdmin)
admin.site.register(RestaurantIntroInfo, RestaurantIntroInfoAdmin)
admin.site.register(DefaultTravelDetailInfo, DefaultTravelDetailInfoAdmin)
admin.site.register(TourCourseDetailInfo, TourCourseDetailInfoAdmin)
admin.site.register(LodgingDetailInfo, LodgingDetailInfoAdmin)
admin.site.register(TravelImageInfo, TravelImageInfoAdmin)
admin.site.register(AreaCodeProgress, AreaCodeProgressAdmin)
admin.site.register(CategoryCodeProgress, CategoryCodeProgressAdmin)
admin.site.register(AdditionalInfoProgress, AdditionalInfoProgressAdmin)
