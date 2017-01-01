from braces.views import LoginRequiredMixin
from braces.views import UserPassesTestMixin
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import UpdateView

from travel_maker.account.forms import UserUpdateForm
from travel_maker.account.models import TmUser


class ProfileHomeView(LoginRequiredMixin, UpdateView):
    model = TmUser
    template_name = 'account/profile.html'
    form_class = UserUpdateForm

    def get_success_url(self):
        return reverse('profile:home', kwargs=self.kwargs)


class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TmUser
    success_url = reverse_lazy('home')

    def test_func(self, user):
        return user == self.get_object()
