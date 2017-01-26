from django.contrib import admin

from travel_maker.travel_schedule.models import TravelSchedule, TravelInfoEvent


class TravelScheduleAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TravelSchedule._meta.fields]
    search_fields = ('title',)


class TravelInfoEventAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TravelInfoEvent._meta.fields]
    search_fields = ('travel_schedule__title',)


admin.site.register(TravelSchedule, TravelScheduleAdmin)
admin.site.register(TravelInfoEvent, TravelInfoEventAdmin)
