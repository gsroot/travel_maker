from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django_summernote.widgets import SummernoteWidget

from travel_maker.travel_review.models import TravelReview


class TravelReviewCreateForm(ModelForm):
    class Meta:
        model = TravelReview
        fields = ['rating', 'tags', 'content']
        widgets = {
            'content': SummernoteWidget()
        }
        labels = {
            'tags': _('여행지의 특징을 태그로 표현해보세요'),
            'content': _('여행 후기를 작성해주세요'),
        }
        help_texts = {
            'tags': _('각 태그는 쉼표(,)로 구분됩니다')
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Field('rating', type='hidden'),
            Field('content'),
        )
