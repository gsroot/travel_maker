from allauth.account.forms import LoginForm, SignupForm
from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, HTML
from django.urls import reverse


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
