from django.contrib import admin

from travel_maker.public_data_collector.models import TravelInfo, NearbySpotInfo


class TravelInfoAdmin(admin.ModelAdmin):
    list_display = ('title', 'addr1')
    search_fields = ('title',)


class NearbySpotInfoAdmin(admin.ModelAdmin):
    list_display = ('center_spot', 'target_spot', 'dist')
    search_fields = ('target_spot__title',)


admin.site.register(TravelInfo, TravelInfoAdmin)
admin.site.register(NearbySpotInfo, NearbySpotInfoAdmin)
