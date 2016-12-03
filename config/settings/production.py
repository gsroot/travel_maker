from .base import *

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['travel_maker.kr', 'www.travel_maker.kr'])


# EMAIL
# ------------------------------------------------------------------------------
DEFAULT_FROM_EMAIL = env('DJANGO_DEFAULT_FROM_EMAIL',
                         default='cookecutter-django <noreply@example.com>')
EMAIL_SUBJECT_PREFIX = env('DJANGO_EMAIL_SUBJECT_PREFIX', default='[cookecutter-django] ')
SERVER_EMAIL = env('DJANGO_SERVER_EMAIL', default=DEFAULT_FROM_EMAIL)

# Anymail with Mailgun
INSTALLED_APPS += ("anymail", )
ANYMAIL = {
    "MAILGUN_API_KEY": env('DJANGO_MAILGUN_API_KEY'),
    "MAILGUN_SENDER_DOMAIN": env('MAILGUN_SENDER_DOMAIN')
}
EMAIL_BACKEND = "anymail.backends.mailgun.MailgunBackend"
