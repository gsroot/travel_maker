# Create your views here.
from statistics import mean

from django.db.models import Avg, Count
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.views.generic import DetailView
from django.views.generic import ListView

from travel_maker.google_data_collector.models import GooglePlaceInfo
from travel_maker.public_data_collector.models import TravelInfo


class TravelInfoLV(ListView):
    queryset = TravelInfo.objects.annotate(review_cnt=Count('googleplaceinfo__googleplacereviewinfo')) \
        .annotate(rating=Coalesce(Avg('googleplaceinfo__googleplacereviewinfo__rating'), Value(0))) \
        .filter(contenttype__name="관광지") \
        .order_by('-rating', '-review_cnt', '-readcount')
    template_name = "travel_info/travelinfo_list.html"
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for info in context['travelinfo_list']:
            info.google_reviews_cnt = info.googleplaceinfo.googleplacereviewinfo_set.count()

        return context


class TravelInfoDV(DetailView):
    model = TravelInfo
    template_name = "travel_info/travelinfo_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if GooglePlaceInfo.objects.filter(travel_info=context['travelinfo']).exists() \
                and context['travelinfo'].googleplaceinfo.googleplacereviewinfo_set.all():
            context['google_reviews'] = context['travelinfo'].googleplaceinfo.googleplacereviewinfo_set.all()
            context['rating'] = mean([review.rating for review in context['google_reviews']])

        return context
