from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.forms import ModelForm
from django_summernote.widgets import SummernoteWidget

from travel_maker.travel_review.models import TravelReview


class TravelReviewCreateForm(ModelForm):
    class Meta:
        model = TravelReview
        fields = ['rating', 'content']
        widgets = {
            'content': SummernoteWidget()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('rating', type='hidden'),
            Field('content'),
        )
