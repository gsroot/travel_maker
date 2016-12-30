from braces.views import LoginRequiredMixin
from django.views.generic import DetailView

from travel_maker.account.models import TmUser


class ProfileHomeView(LoginRequiredMixin, DetailView):
    model = TmUser
    template_name = 'account/profile.html'
