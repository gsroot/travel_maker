from django.contrib import admin

from travel_maker.travel_bookmark.models import TravelBookmark, ScheduleBookmark


class TravelBookmarkAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TravelBookmark._meta.fields]
    search_fields = ('travel_info__title',)


class ScheduleBookmarkAdmin(admin.ModelAdmin):
    list_display = [f.name for f in ScheduleBookmark._meta.fields]
    search_fields = ('travel_schedule__title',)


admin.site.register(TravelBookmark, TravelBookmarkAdmin)
admin.site.register(ScheduleBookmark, ScheduleBookmarkAdmin)
