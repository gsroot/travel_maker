from allauth.account.forms import LoginForm, SignupForm
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.forms import ModelForm, Textarea
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from travel_maker.account.models import TmUser


class UserSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('account_signup')
        self.helper.layout = Layout(
            Fieldset(
                '',
                'email',
                'username',
                'password1',
                'password2',

            ),
            FormActions(
                HTML('<button class="btn btn-primary btn-block" id="id-signup" type="submit">회원가입</button>'),
                css_class='text-center'
            ),
        )


class UserLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('account_login')
        self.helper.layout = Layout(
            Fieldset(
                '',
                'login',
                'password',
                'remember',
            ),
            FormActions(
                HTML('<button class="btn btn-primary btn-block" id="id-login" type="submit">로그인</button>'),
                css_class='text-center'
            ),
        )


class UserUpdateForm(ModelForm):
    class Meta:
        model = TmUser
        fields = ['username', 'image', 'introduction']
        widgets = {
            'introduction': Textarea(),
        }
        labels = {
            'image': _("프로필 사진"),
            'introduction': _("자기소개"),
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if not image:
            return image

        if image.size > 2 * 1024 * 1024:
            raise ValidationError("프로필 이미지는 2MB 이하의 이미지만 허용됩니다.")

        width, height = get_image_dimensions(image)
        if width < 50 or height < 50:
            raise ValidationError(
                "프로필 이미지 최소 사이즈는 50x50 입니다. 선택하신 이미지 사이즈는 {0}x{1} 입니다.".format(
                    width, height
                )
            )
        elif width > 1000 or height > 1000:
            raise ValidationError(
                "프로필 이미지 최대 사이즈는 1000x1000 입니다. 선택하신 이미지 사이즈는 {0}x{1} 입니다.".format(
                    width, height
                )
            )

        return image
