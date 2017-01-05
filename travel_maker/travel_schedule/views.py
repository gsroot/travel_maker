from braces.views import LoginRequiredMixin
from braces.views import UserPassesTestMixin
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.views.generic import DeleteView
from django.views.generic import DetailView
from django.views.generic import ListView
from django.views.generic import UpdateView
from rest_framework.generics import UpdateAPIView

from travel_maker.public_data_collector.models import TravelInfo, Area, ContentType
from travel_maker.travel_schedule.forms import TravelScheduleForm
from travel_maker.travel_schedule.models import TravelSchedule
from travel_maker.travel_schedule.serializers import TravelCalendarSerializer, TravelScheduleSerializer


class TravelScheduleListView(LoginRequiredMixin, ListView):
    paginate_by = 10

    def get_queryset(self):
        queryset = TravelSchedule.objects.filter(owner=self.request.user)

        return queryset


class TravelScheduleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TravelSchedule

    def test_func(self, user):
        return user == self.get_object().owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['travelschedule'].duration_days = \
            (context['travelschedule'].end - context['travelschedule'].start).days + 1

        return context


class TravelScheduleCreateView(LoginRequiredMixin, CreateView):
    model = TravelSchedule
    form_class = TravelScheduleForm

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.owner = self.request.user
        instance.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('travel_schedule:detail', args=(self.object.id,))


class TravelScheduleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = TravelSchedule
    form_class = TravelScheduleForm
    template_name_suffix = '_update'

    def test_func(self, user):
        return user == self.get_object().owner

    def get_success_url(self):
        return reverse('travel_schedule:detail', kwargs=self.kwargs)


class TravelCalendarUpdateView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = TravelSchedule
    template_name = 'travel_schedule/travelschedule_calendar_update.html'

    def test_func(self, user):
        return user == self.get_object().owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['travelschedule'].duration_days = \
            (context['travelschedule'].end - context['travelschedule'].start).days + 1
        context['area_list'] = Area.objects.all()
        context['contenttype_list'] = ContentType.objects.filter(name__in=['관광지', '숙박', '쇼핑', '음식점'])
        context['travelinfo_list'] = TravelInfo.objects.filter(contenttype__in=context['contenttype_list'])[:20]

        return context


class TravelScheduleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = TravelSchedule
    success_url = reverse_lazy('travel_schedule:list')

    def test_func(self, user):
        return user == self.get_object().owner


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
