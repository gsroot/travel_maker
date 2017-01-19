from braces.views import LoginRequiredMixin
from braces.views import UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import ListView

from travel_maker.travel_bookmark.models import TravelBookmark, ScheduleBookmark


class TravelBookmarkCreateView(LoginRequiredMixin, CreateView):
    model = TravelBookmark
    fields = ['travel_info']

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.owner = self.request.user
        if TravelBookmark.objects.filter(owner=instance.owner, travel_info=instance.travel_info).exists():
            messages.warning(self.request, '이미 관심여행지에 등록되어 있습니다')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
        instance.save()
        messages.success(self.request, '관심여행지에 등록 되었습니다')

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class TravelBookmarkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TravelBookmark

    def test_func(self, user):
        return user == self.get_object().owner

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class ScheduleBookmarkCreateView(LoginRequiredMixin, CreateView):
    model = ScheduleBookmark
    fields = ['travel_schedule']

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.owner = self.request.user
        if ScheduleBookmark.objects.filter(owner=instance.owner, travel_schedule=instance.travel_schedule).exists():
            messages.warning(self.request, '이미 책갈피에 등록되어 있습니다')
            return HttpResponseRedirect(self.request.META.get('HTTP_REFERER'))
        instance.save()
        messages.success(self.request, '책갈피에 등록 되었습니다')

        return super().form_valid(form)

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')


class ScheduleBookmarkDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ScheduleBookmark

    def test_func(self, user):
        return user == self.get_object().owner

    def get_success_url(self):
        return self.request.user.get_absolute_url()
