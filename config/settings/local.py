from .base import *

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool('DEBUG', default=True)
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG

ALLOWED_HOSTS = ['*']

# Mail settings
# ------------------------------------------------------------------------------

EMAIL_PORT = 1025

EMAIL_HOST = 'localhost'
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND',
                    default='django.core.mail.backends.console.EmailBackend')

# Your local stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------
