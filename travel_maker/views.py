from django.views.generic import FormView

from travel_maker.account.forms import UserLoginForm
from travel_maker.public_data_collector.models import TravelInfo


class HomeView(FormView):
    form_class = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['top6_tourspot_list'] = TravelInfo.objects.filter(
            contenttype__name='관광지', image__isnull=False
        ).exclude(image='')[:6]

        return context

    def get_template_names(self):
        if self.request.user.is_authenticated():
            self.request.user.update_profile()

            return 'pages/home.html'
        else:
            return 'pages/anonymous_home.html'
