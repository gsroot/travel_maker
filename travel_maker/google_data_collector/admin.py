from django.contrib import admin

from travel_maker.google_data_collector.models import GooglePlaceInfo, GooglePlaceReviewInfo, GoogleApiProgress


class GooglePlaceInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GooglePlaceInfo._meta.fields]
    search_fields = ('travel_info__title',)


class GooglePlaceReviewInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GooglePlaceReviewInfo._meta.fields]
    search_fields = ('place_info__travel_info__title',)


class GoogleApiProgressAdmin(admin.ModelAdmin):
    list_display = [f.name for f in GoogleApiProgress._meta.fields]


admin.site.register(GooglePlaceInfo, GooglePlaceInfoAdmin)
admin.site.register(GooglePlaceReviewInfo, GooglePlaceReviewInfoAdmin)
admin.site.register(GoogleApiProgress, GoogleApiProgressAdmin)
