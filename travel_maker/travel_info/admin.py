from django.contrib import admin

from travel_maker.public_data_collector.models import TravelInfo, NearbySpotInfo


class TravelInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TravelInfo._meta.fields]
    search_fields = ('title',)


class NearbySpotInfoAdmin(admin.ModelAdmin):
    list_display = [f.name for f in NearbySpotInfo._meta.fields]
    search_fields = ('target_spot__title',)


admin.site.register(TravelInfo, TravelInfoAdmin)
admin.site.register(NearbySpotInfo, NearbySpotInfoAdmin)
