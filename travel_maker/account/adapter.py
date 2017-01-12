from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import user_email, user_username
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
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
        initial = {
            'email': user_email(user) or '',
            'username': user_username(user).split('@')[0] or '',
        }
        return initial

    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        user.username = user.email.split('@')[0]
        return user
