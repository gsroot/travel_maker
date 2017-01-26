from django.contrib import admin

from travel_maker.data_analysis.models import DataAnalysisProgress


class DataAnalysisProgressAdmin(admin.ModelAdmin):
    list_display = [f.name for f in DataAnalysisProgress._meta.fields]


admin.site.register(DataAnalysisProgress, DataAnalysisProgressAdmin)
