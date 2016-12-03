# Create your views here.
from django.views.generic import DetailView
from django.views.generic import ListView

from travel_maker.public_data_collector.models import TravelInfo


class TravelInfoLV(ListView):
    model = TravelInfo
    template_name = "travel_info/travelinfo_list.html"
    paginate_by = 10


class TravelInfoDV(DetailView):
    model = TravelInfo
    template_name = "travel_info/travelinfo_detail.html"