# Create your views here.
from statistics import mean

from django.db.models import Avg, Count
from django.db.models import Value
from django.db.models.functions import Coalesce
from django.views.generic import DetailView
from django.views.generic import ListView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from config.settings.base import NAVER_API_CLIENT_ID
from travel_maker.google_data_collector.models import GooglePlaceInfo
from travel_maker.public_data_collector.models import TravelInfo, Area
from travel_maker.travel_info.forms import TravelInfoSearchForm


class TravelInfoLV(ListView):
    template_name = "travel_info/travelinfo_list.html"
    paginate_by = 10

    def get_queryset(self):
        queryset = TravelInfo.objects.all()

        if self.request.GET.get('area'):
            queryset = queryset.filter(sigungu__area=self.request.GET.get('area'))

        if self.request.GET.getlist('contenttype'):
            queryset = queryset.filter(contenttype__in=self.request.GET.getlist('contenttype'))

        if self.request.GET.get('name'):
            queryset = queryset.filter(title__contains=self.request.GET.get('name'))

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.request.GET)
        if self.request.GET.get('area'):
            context['map_areas'] = Area.objects.filter(id=self.request.GET.get('area'))
        else:
            context['map_areas'] = Area.objects.all()
        context['center_mapx'] = mean([area.info.mapx for area in context['map_areas']])
        context['center_mapy'] = mean([area.info.mapy for area in context['map_areas']])
        context['naverapi_client_id'] = NAVER_API_CLIENT_ID
        context['form'] = TravelInfoSearchForm(self.request.GET) \
            if any([v != '' for v in self.request.GET.values()]) else TravelInfoSearchForm()

        for info in context['travelinfo_list']:
            info.google_reviews_cnt = info.googleplaceinfo.googleplacereviewinfo_set.count() \
                if GooglePlaceInfo.objects.filter(travel_info=info).exists() else 0

        return context


class TravelInfoDV(DetailView):
    model = TravelInfo
    template_name = "travel_info/travelinfo_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['naverapi_client_id'] = NAVER_API_CLIENT_ID

        if GooglePlaceInfo.objects.filter(travel_info=context['travelinfo']).exists() \
                and context['travelinfo'].googleplaceinfo.googleplacereviewinfo_set.all():
            context['google_reviews'] = context['travelinfo'].googleplaceinfo.googleplacereviewinfo_set.all()

        return context


class TravelInfoList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'travel_info/travelinfo_list_by_api.html'

    def get_queryset(self):
        queryset = TravelInfo.objects.filter(contenttype__name__in=['관광지', '숙박', '쇼핑', '음식점'])
        area = self.request.query_params.get('area')
        title = self.request.query_params.get('name')
        contenttype_list = self.request.query_params.getlist('contenttype_list[]')
        page = int(self.request.query_params.get('page', 1))
        if area:
            queryset = queryset.filter(sigungu__area=int(area))
        if title:
            queryset = queryset.filter(title__contains=title)
        if contenttype_list:
            queryset = queryset.filter(contenttype__in=contenttype_list)

        queryset = queryset[20 * (page - 1):20 * page]
        return queryset

    def get(self, request):
        return Response({'travelinfo_list': self.get_queryset()})
