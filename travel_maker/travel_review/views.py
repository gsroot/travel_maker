from braces.views import LoginRequiredMixin
from braces.views import UserPassesTestMixin
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView

from travel_maker.public_data_collector.models import TravelInfo
from travel_maker.travel_review.forms import TravelReviewCreateForm
from travel_maker.travel_review.models import TravelReview


class TravelReviewDetailView(DetailView):
    model = TravelReview


class TravelReviewCreateView(LoginRequiredMixin, CreateView):
    model = TravelReview
    form_class = TravelReviewCreateForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.travel_info = TravelInfo.objects.get(id=self.kwargs['travel_info'])
        instance.owner = self.request.user
        instance.save()

        return super().form_valid(form)

    def get_success_url(self):
        self.kwargs['pk'] = self.kwargs.pop('travel_info')
        return reverse('travel_info:detail', kwargs=self.kwargs)

    def get(self, request, *args, **kwargs):
        if TravelReview.objects.filter(travel_info=self.kwargs['travel_info'], owner=request.user).exists():
            messages.warning(request, '이미 해당 여행지에 대한 리뷰를 작성 하셨습니다')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return super().get(request, *args, **kwargs)


class TravelReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TravelReview

    def test_func(self, user):
        return user == self.get_object().owner

    def get_success_url(self):
        return reverse('travel_info:detail', args=(self.get_object().travel_info.id,))
