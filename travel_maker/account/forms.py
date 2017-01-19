from allauth.account import app_settings
from allauth.account.forms import LoginForm, SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.forms import ModelForm, Textarea, CharField, TextInput
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from travel_maker.account.models import TmUser


class UserSignupForm(SignupForm):
    username = CharField(
        label=_("닉네임"), min_length=app_settings.USERNAME_MIN_LENGTH,
        widget=TextInput(attrs={'placeholder': _('닉네임'), 'autofocus': 'autofocus'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                'email',
                'username',
                'password1',
                'password2',

            ),
            FormActions(
                HTML('<button class="btn btn-tm-default btn-block" id="id-signup" type="submit">회원가입</button>'),
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
            ),
            FormActions(
                HTML('<button class="btn btn-tm-default btn-block" id="id-login" type="submit">로그인</button>'),
                css_class='text-center'
            ),
        )

    def clean_login(self):
        login = super().clean_login()
        users = TmUser.objects.filter(email=login)
        if users.exists() and users[0].is_social:
            raise ValidationError('해당 이메일은 연동된 소셜 계정이 존재합니다. 소셜 계정으로 로그인 해주세요.')

        return login


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


class SocialUserSignupForm(SocialSignupForm):
    username = CharField(
        label=_("닉네임"), min_length=app_settings.USERNAME_MIN_LENGTH,
        widget=TextInput(attrs={'placeholder': _('닉네임'), 'autofocus': 'autofocus'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                '',
                'email',
                'username',

            ),
            FormActions(
                HTML('<button class="btn btn-tm-default btn-block" id="id-signup" type="submit">회원가입</button>'),
                css_class='text-center'
            ),
        )
