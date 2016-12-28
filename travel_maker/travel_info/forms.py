from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Field, Div, HTML
from django.forms import RadioSelect, ModelChoiceField, CharField, Form

from travel_maker.public_data_collector.models import Area, ContentType


class TmChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.name


class TravelInfoSearchForm(Form):
    area = TmChoiceField(
        queryset=Area.objects.all(), required=False, widget=RadioSelect(), label='지역', empty_label='전체',
    )
    contenttype = TmChoiceField(
        queryset=ContentType.objects.all(), required=False, widget=RadioSelect(), label='여행지 타입', empty_label='전체'
    )
    name = CharField(max_length=200, required=False, label='여행지 이름')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            Fieldset(
                '',
                Field('area', template='crispy_forms/custom_choice_field.html'),
                Field('contenttype', template='crispy_forms/custom_choice_field.html'),
                Div(
                    Div(css_class='col-md-3'),
                    Div('name', css_class='col-md-6'),
                    Div(css_class='col-md-3'),
                    css_class='row'
                ),
                FormActions(
                    HTML('<button class="btn btn-primary" id="id-submit" type="submit">'
                         '<i class="fa fa-search search"></i>검색</button>'),
                    css_class='text-center'
                ),
                css_class='row'

            )
        )
