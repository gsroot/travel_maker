from django.db.models import Count
from django.views.generic import FormView

from travel_maker.account.forms import UserLoginForm
from travel_maker.public_data_collector.models import TravelInfo
from travel_maker.travel_review.models import TravelReview
from travel_maker.travel_schedule.models import TravelSchedule


class HomeView(FormView):
    form_class = UserLoginForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['popular_tourspot_list_1'] = TravelInfo.objects.filter(
            contenttype__name='관광지', image__isnull=False
        ).exclude(image='').annotate(score_cnt=Count('score')).order_by('-score_cnt', '-score', 'id')[:24]
        context['popular_tourspot_list_2'] = context['popular_tourspot_list_1'][:6]

        context['popular_travelschedule_list'] = TravelSchedule.objects.filter(is_public=True).order_by(
            '-updown_likes')[:12]

        context['recent_review_list'] = TravelReview.objects.all().order_by('-updown_likes')[:12]

        return context

    def get_template_names(self):
        if self.request.user.is_authenticated():
            return 'pages/home.html'
        else:
            return 'pages/anonymous_home.html'
