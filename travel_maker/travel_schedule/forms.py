from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div, HTML
from django import forms

from travel_maker.travel_schedule.models import TravelSchedule


class TravelScheduleForm(forms.ModelForm):
    class Meta:
        model = TravelSchedule
        fields = ['title', 'description', 'start', 'end', 'people_count', 'tags']
        widgets = {
            'start': forms.DateInput(attrs={'readonly': 'true'}),
            'end': forms.DateInput(attrs={'readonly': 'true'}),
            'people_count': forms.NumberInput(attrs={'min': '1', 'max': '100'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('title'),
                Field('description'),
                Div(
                    Div(Field('start'), css_class='col-md-4'),
                    Div(Field('end'), css_class='col-md-4'),
                    Div(Field('people_count'), css_class='col-md-4'),
                    css_class='row',
                ),
                Field('tags')
            )
        )


class TravelScheduleSearchForm(forms.Form):
    all = 'all'
    before = 'before'
    ing = 'ing'
    after = 'after'
    TRAVEL_STATUS = (
        (all, '전체'),
        (before, '여행전'),
        (ing, '여행중'),
        (after, '여행후')
    )
    travel_status = forms.ChoiceField(choices=TRAVEL_STATUS, required=False, label='여행구분')
    duration_days_min = forms.IntegerField(min_value=1, max_value=30, required=False, widget=forms.HiddenInput())
    duration_days_max = forms.IntegerField(min_value=1, max_value=30, required=False, widget=forms.HiddenInput())
    keyword = forms.CharField(required=False, label='키워드')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Div(
                Div(css_class='col-md-3'),
                Div(
                    Field('travel_status'),
                    HTML('<label for="duration-days" class="control-label">여행기간</label>'),
                    Div(css_id='duration-days'),
                    Div(css_class='spacer-xs'),
                    Div(
                        Div(HTML('1일'), css_id='day-min', css_class='col-md-2'),
                        Div(css_class='col-md-8'),
                        Div(HTML('30일'), css_id='day-max', css_class='col-md-2'),
                        css_class='row'
                    ),
                    Field('duration_days_min'),
                    Field('duration_days_max'),
                    Div(css_class='spacer-xs'),
                    Field('keyword'),
                    css_class='col-md-6'
                ),
                css_class='row'
            ),
            FormActions(
                HTML('<button class="btn btn-primary" id="id-submit" type="submit">'
                     '<i class="fa fa-search search"></i>검색</button>'),
                css_class='center'
            )
        )
