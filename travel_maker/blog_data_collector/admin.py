from django.contrib import admin

from travel_maker.blog_data_collector.models import BlogData, BlogDataProgress


class BlogDataAdmin(admin.ModelAdmin):
    list_display = [f.name for f in BlogData._meta.fields]
    search_fields = ('travel_info__title',)


class BlogDataProgressAdmin(admin.ModelAdmin):
    list_display = [f.name for f in BlogDataProgress._meta.fields]


admin.site.register(BlogData, BlogDataAdmin)
admin.site.register(BlogDataProgress, BlogDataProgressAdmin)
