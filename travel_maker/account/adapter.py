from allauth.account import app_settings as account_settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_username
from allauth.socialaccount import app_settings
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.utils import email_address_exists
from django.contrib import messages
from django.forms import forms


class AccountAdapter(DefaultAccountAdapter):
    def clean_username(self, username, shallow=False):
        if not self.username_regex.match(username):
            raise forms.ValidationError(
                self.error_messages['invalid_username'])

        return username


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_signup_form_initial_data(self, sociallogin):
        user = sociallogin.user
        user.is_social = True
        initial = {
            'email': user_email(user) or '',
            'username': user_username(user).split('@')[0] or '',
        }
        return initial

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email.split('@')[0]
        return user

    def is_auto_signup_allowed(self, request, sociallogin):
        auto_signup = app_settings.AUTO_SIGNUP
        if auto_signup:
            email = user_email(sociallogin.user)
            if email:
                if account_settings.UNIQUE_EMAIL:
                    if email_address_exists(email):
                        auto_signup = False
                        messages.error(request, '해당 이메일 계정은 이미 회원가입이 되어 있습니다.'
                                                ' 소셜 로그인이 아닌 사이트 자체 로그인을 사용해 주세요.')
            elif app_settings.EMAIL_REQUIRED:
                auto_signup = False
        return auto_signup
