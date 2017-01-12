from allauth.account.forms import ChangePasswordForm
from allauth.account.views import PasswordChangeView
from braces.views import LoginRequiredMixin
from braces.views import UserPassesTestMixin
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import UpdateView

from travel_maker.account.forms import UserUpdateForm
from travel_maker.account.models import TmUser


class ProfileHomeView(LoginRequiredMixin, UpdateView):
    model = TmUser
    template_name = 'account/profile.html'
    form_class = UserUpdateForm

    def get_success_url(self):
        return reverse('profile:home', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['passwordchangeform'] = ChangePasswordForm()

        return context


class ProfilePasswordChangeView(LoginRequiredMixin, UserPassesTestMixin, PasswordChangeView):
    template_name = 'account/profile.html'

    def test_func(self, user):
        return not user.is_social

    def get_success_url(self):
        return reverse('profile:home', kwargs=self.kwargs)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=UserUpdateForm(), passwordchangeform=form))


class ProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TmUser
    success_url = reverse_lazy('home')

    def test_func(self, user):
        return user == self.get_object()
