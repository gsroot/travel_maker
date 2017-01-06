import os

import requests
from PIL import Image
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator, ASCIIUsernameValidator
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db import models
from django.db.models import ImageField, PositiveIntegerField
from django.utils import six
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from config.settings.base import MEDIA_ROOT


class TmUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        user = self.model(username=username, email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **kwargs):
        user = self.model(username=username, email=email, is_staff=True, is_superuser=True, **kwargs)
        user.set_password(password)
        user.save()
        return user


def image_path(instance, filename):
    name, ext = os.path.splitext(filename)
    return 'img/users/{0}/profile{1}'.format(instance.id, ext)


def thumbnail_path(instance, filename):
    return 'img/users/{0}/thumbnail.png'.format(instance.id)


class TmUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('닉네임'),
        max_length=150,
        default='',
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
    )
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    image_width = PositiveIntegerField(editable=False, null=True)
    image_height = PositiveIntegerField(editable=False, null=True)
    image = ImageField(
        upload_to=image_path, height_field='image_height', width_field='image_width', blank=True
    )
    thumbnail_width = PositiveIntegerField(editable=False, null=True)
    thumbnail_height = PositiveIntegerField(editable=False, null=True)
    thumbnail = ImageField(
        upload_to=thumbnail_path, height_field='thumbnail_height', width_field='thumbnail_width', blank=True
    )
    introduction = models.CharField(max_length=2000, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = TmUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    @property
    def social_account(self):
        if self.socialaccount_set.all():
            return self.socialaccount_set.all()[0]
        else:
            return None

    @classmethod
    def from_db(cls, db, field_names, values):
        new_obj = super().from_db(db, field_names, values)
        new_obj._loaded_image = values[field_names.index('image')]
        return new_obj

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def update_image_by_facebook(self):
        url = 'http://graph.facebook.com/v2.8/{}/picture?type=large'.format(self.social_account.uid)
        image_data = requests.get(url)
        image_file = ContentFile(image_data.content)
        if not self.image:
            self.image.save('profile.jpg', image_file, save=False)
            self.update_thumbnail()
            self.save()

    def update_thumbnail(self):
        if hasattr(self, '_loaded_image') and self._loaded_image:
            os.remove(MEDIA_ROOT + '/' + self._loaded_image)
        if self.image:
            self.image.open()
            image = Image.open(self.image)
            side_length = min([self.image_width, self.image_height])
            croped = image.crop((0, 0, side_length, side_length))

            filepath = MEDIA_ROOT + '/' + thumbnail_path(self, None)
            croped.thumbnail((200, 200))
            croped.save(filepath, 'PNG')

            url = thumbnail_path(self, None)
            self.thumbnail = url
        else:
            self.thumbnail = ''

    def save(self, *args, **kwargs):
        if not self._state.adding:
            if self.social_account and self.social_account.provider == 'facebook' \
                    and not hasattr(self, '_loaded_image') and not self.image:
                self.update_image_by_facebook()
            elif hasattr(self, '_loaded_image') and self.image != self._loaded_image:
                self.update_thumbnail()

        return super().save(*args, **kwargs)
