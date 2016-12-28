from django.views.generic import FormView

from travel_maker.account.forms import UserLoginForm
from travel_maker.public_data_collector.models import TravelInfo


class HomeView(FormView):
    template_name = 'pages/home.html'
    form_class = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top6_tourspot_list'] = TravelInfo.objects.filter(
            contenttype__name='관광지', image__isnull=False
        ).exclude(image='')[:6]

        return context
