from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div
from django.forms import ModelForm, DateInput, NumberInput

from travel_maker.travel_schedule.models import TravelSchedule


class TravelScheduleForm(ModelForm):
    class Meta:
        model = TravelSchedule
        fields = ['title', 'description', 'start', 'end', 'people_count', 'tags']
        widgets = {
            'start': DateInput(attrs={'readonly': 'true'}),
            'end': DateInput(attrs={'readonly': 'true'}),
            'people_count': NumberInput(attrs={'min': '1', 'max': '100'}),
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
