# Create your views here.
from statistics import mean

from django.db.models import F
from django.db.models import Q
from django.views.generic import DetailView
from django.views.generic import ListView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from config.settings.base import NAVER_API_CLIENT_ID
from travel_maker.blog_data_collector.models import BlogData
from travel_maker.public_data_collector.models import TravelInfo, NearbySpotInfo
from travel_maker.travel_info.forms import TravelInfoSearchForm


class TravelInfoListView(ListView):
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
        travelinfo_list = context['travelinfo_list']
        spot_mapx_list = [spot.mapx for spot in travelinfo_list if spot.mapx]
        spot_mapy_list = [spot.mapy for spot in travelinfo_list if spot.mapy]
        context['center_mapx'] = mean(spot_mapx_list) if spot_mapx_list else 0
        context['center_mapy'] = mean(spot_mapy_list) if spot_mapy_list else 0
        context['naverapi_client_id'] = NAVER_API_CLIENT_ID
        context['form'] = TravelInfoSearchForm(self.request.GET) \
            if any([v != '' for v in self.request.GET.values()]) else TravelInfoSearchForm()

        return context


class TravelInfoDetailView(DetailView):
    model = TravelInfo
    template_name = 'travel_info/travelinfo_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['viewtype'] = self.request.GET.get('viewtype')
        context['naverapi_client_id'] = NAVER_API_CLIENT_ID

        if hasattr(context['travelinfo'], 'googleplaceinfo'):
            context['google_reviews'] = [review.set_does_user_already_vote(self.request.user) for review in
                                         context['travelinfo'].googleplaceinfo.googleplacereviewinfo_set.all()]

        context['travel_reviews'] = [review.set_does_user_already_vote(self.request.user) for review in
                                     context['travelinfo'].travelreview_set.all()]

        return context


class NearbySpotInfoListView(ListView):
    template_name = 'travel_info/snippets/item_nearby_info.html'
    paginate_by = 12

    def get_queryset(self):
        travel_info = TravelInfo.objects.filter(id=self.kwargs['pk']).exclude(contenttype__name='여행코스')
        if not travel_info:
            return []
        queryset = NearbySpotInfo.objects.filter(target_spot=travel_info).exclude(
            Q(center_spot=F('target_spot')) | Q(center_spot__contenttype__name='여행코스') | Q(dist=0)
        ).order_by('dist')
        return queryset


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


class NearbySpotInfoList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'travel_info/travelinfo_list_by_api.html'

    def get_queryset(self, pk):
        queryset = TravelInfo.objects.filter(contenttype__name__in=['관광지', '숙박', '쇼핑', '음식점'])
        page = int(self.request.query_params.get('page', 1))
        queryset = queryset[20 * (page - 1):20 * page]
        return queryset

    def get(self, request, pk):
        return Response({'travelinfo_list': self.get_queryset(pk)})


class BlogList(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'travel_info/blog_list_by_api.html'

    def get_queryset(self):
        queryset = BlogData.objects.filter(travel_info=self.kwargs['pk'])
        page = int(self.request.query_params.get('page', 1))
        queryset = queryset[10 * (page - 1):10 * page]
        return queryset

    def get(self, request, pk):
        return Response({'blog_list': self.get_queryset()})
