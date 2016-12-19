from django.forms import ModelForm

from travel_maker.blog_data_collector.models import BlogData


class BlogDataForm(ModelForm):
    class Meta:
        model = BlogData
        fields = '__all__'
