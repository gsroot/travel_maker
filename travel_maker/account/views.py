from allauth.account.forms import ChangePasswordForm
from allauth.account.views import PasswordChangeView
from braces.views import LoginRequiredMixin
from braces.views import UserPassesTestMixin
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.urls import reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic import UpdateView
from updown.models import Vote

from travel_maker.account.forms import UserUpdateForm
from travel_maker.account.models import TmUser
from travel_maker.google_data_collector.models import GooglePlaceReviewInfo
from travel_maker.travel_bookmark.models import TravelBookmark, ScheduleBookmark
from travel_maker.travel_review.models import TravelReview
from travel_maker.travel_schedule.models import TravelSchedule


class ProfileHomeView(LoginRequiredMixin, UpdateView):
    model = TmUser
    template_name = 'account/profile.html'
    form_class = UserUpdateForm

    def get_success_url(self):
        messages.success(self.request, '회원 정보가 설정 되었습니다')
        return reverse('profile:home', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['passwordchangeform'] = ChangePasswordForm()
        user_id = self.kwargs['pk']
        context['schedule_cnt'] = TravelSchedule.objects.filter(owner=user_id).count()
        context['travelbookmark_cnt'] = TravelBookmark.objects.filter(owner=user_id).count()
        context['schedulebookmark_cnt'] = ScheduleBookmark.objects.filter(owner=user_id).count()

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


class ProfileScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'travel_schedule/snippets/profileschedule_list.html'

    def get_queryset(self):
        is_mine = self.request.user.id == int(self.kwargs['pk'])
        queryset = TravelSchedule.objects.filter(owner=self.kwargs['pk']) \
            if is_mine else TravelSchedule.objects.filter(owner=self.kwargs['pk'], is_public=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['tmuser'] = TmUser.objects.get(id=self.kwargs['pk'])
        return context


class ProfileTravelBookmarkListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        queryset = TravelBookmark.objects.filter(owner=self.kwargs['pk'])
        return queryset


class ProfileScheduleBookmarkListView(LoginRequiredMixin, ListView):
    def get_queryset(self):
        queryset = ScheduleBookmark.objects.filter(owner=self.kwargs['pk'])
        return queryset


class UpdownListView(LoginRequiredMixin, ListView):
    template_name = 'updown/updown_list.html'

    def get_queryset(self):
        queryset = Vote.objects.filter(user=self.kwargs['pk'])
        return queryset


class ProfileScheduleUpdownScoreView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        schedule = TravelSchedule.objects.get(id=kwargs['schedule_id'])
        score = 1 if schedule.get_does_user_already_vote(request.user) else 0
        return HttpResponse(score)


class ProfileReviewUpdownScoreView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        review = TravelReview.objects.get(id=kwargs['review_id'])
        score = 1 if review.get_does_user_already_vote(request.user) else 0
        return HttpResponse(score)


class ProfileGoogleReviewUpdownScoreView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        review = GooglePlaceReviewInfo.objects.get(id=kwargs['review_id'])
        score = 1 if review.get_does_user_already_vote(request.user) else 0
        return HttpResponse(score)
