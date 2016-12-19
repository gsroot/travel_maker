from django.views.generic import FormView

from travel_maker.account.forms import UserLoginForm


class HomeView(FormView):
    template_name = 'pages/home.html'
    form_class = UserLoginForm
