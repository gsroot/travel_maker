from braces.views import LoginRequiredMixin
from braces.views import UserPassesTestMixin
from datetime import date
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from rest_framework.generics import UpdateAPIView

from travel_maker.public_data_collector.models import TravelInfo, Area, ContentType
from travel_maker.travel_schedule.forms import TravelScheduleForm, TravelScheduleSearchForm
from travel_maker.travel_schedule.models import TravelSchedule
from travel_maker.travel_schedule.serializers import TravelCalendarSerializer, TravelScheduleSerializer


class TravelScheduleListView(LoginRequiredMixin, ListView):
    template_name = 'travel_schedule/travelschedule_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = TravelSchedule.objects.filter(is_public=True)

        travel_status = self.request.GET.get('travel_status')
        if travel_status:
            today = date.today()
            if travel_status == TravelScheduleSearchForm.before:
                queryset = queryset.filter(start__gt=today)
            elif travel_status == TravelScheduleSearchForm.ing:
                queryset = queryset.filter(start__lte=today, end__gte=today)
            elif travel_status == TravelScheduleSearchForm.after:
                queryset = queryset.filter(end__lt=today)

        duration_days_min = self.request.GET.get('duration_days_min')
        if duration_days_min:
            duration_days_min = int(duration_days_min)
            queryset = queryset.filter(
                id__in=[schedule.id for schedule in queryset if schedule.duration_days >= duration_days_min]
            )

        duration_days_max = self.request.GET.get('duration_days_max')
        if duration_days_max:
            duration_days_max = int(duration_days_max)
            queryset = queryset.filter(
                id__in=[schedule.id for schedule in queryset if schedule.duration_days <= duration_days_max]
            )

        keyword = self.request.GET.get('keyword')
        if keyword:
            queryset = queryset.filter(title__contains=keyword)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.request.GET)
        context['form'] = TravelScheduleSearchForm(self.request.GET) \
            if any([v != '' for v in self.request.GET.values()]) else TravelScheduleSearchForm()
        return context


class TravelScheduleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TravelSchedule

    def test_func(self, user):
        return user == self.get_object().owner or self.get_object().is_public


class TravelScheduleCreateView(LoginRequiredMixin, CreateView):
    model = TravelSchedule
    form_class = TravelScheduleForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.owner = self.request.user
        instance.save()

        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, '여행 일정이 생성 되었습니다')
        return reverse('travel_schedule:detail', args=(self.object.id,))

    def get(self, request, *args, **kwargs):
        travel_schedule_cnt = self.model.objects.filter(owner=request.user).count()
        if travel_schedule_cnt >= 20:
            messages.warning(request, '계정당 최대 20개까지만 여행 일정을 만들 수 있습니다')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        return super().get(request, *args, **kwargs)


class TravelScheduleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TravelSchedule
    form_class = TravelScheduleForm
    template_name_suffix = '_update'

    def test_func(self, user):
        return user == self.get_object().owner

    def get_success_url(self):
        messages.success(self.request, '여행 일정 정보가 설정되었습니다')
        return reverse('travel_schedule:detail', kwargs=self.kwargs)


class TravelCalendarUpdateView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TravelSchedule
    template_name = 'travel_schedule/travelschedule_calendar_update.html'

    def test_func(self, user):
        return user == self.get_object().owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['area_list'] = Area.objects.all()
        context['contenttype_list'] = ContentType.objects.filter(name__in=['관광지', '숙박', '쇼핑', '음식점'])
        context['travelinfo_list'] = TravelInfo.objects.filter(contenttype__in=context['contenttype_list'])[:20]

        return context


class TravelScheduleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TravelSchedule

    def test_func(self, user):
        return user == self.get_object().owner

    def get_success_url(self):
        return self.request.user.get_absolute_url()


class TravelScheduleUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateAPIView):
    queryset = TravelSchedule.objects.all()
    serializer_class = TravelScheduleSerializer

    def test_func(self, user):
        return user == self.get_object().owner


class TravelCalendarUpdate(LoginRequiredMixin, UserPassesTestMixin, UpdateAPIView):
    queryset = TravelSchedule.objects.all()
    serializer_class = TravelCalendarSerializer

    def test_func(self, user):
        return user == self.get_object().owner
