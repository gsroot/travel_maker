from django.contrib import admin

from travel_maker.travel_review.models import TravelReview


class TravelReviewAdmin(admin.ModelAdmin):
    list_display = [f.name for f in TravelReview._meta.fields]
    search_fields = ('travel_info__title',)


admin.site.register(TravelReview, TravelReviewAdmin)
