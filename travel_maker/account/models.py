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
from io import BytesIO


class TmUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **kwargs):
        user = self.model(username=username, email=email, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password, **kwargs):
        user = self.model(username=username, email=email, is_staff=True, is_superuser=True, **kwargs)
        user.set_password(password)
        print(username, email, password)
        user.save()
        return user


def user_img_directory_path(instance, filename):
    return 'img/users/{0}/{1}'.format(instance.id, filename)


class TmUser(AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator() if six.PY3 else ASCIIUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(_('email address'), max_length=255, unique=True)
    image_width = PositiveIntegerField(editable=False, default=120)
    image_height = PositiveIntegerField(editable=False, default=120)
    image = ImageField(
        upload_to=user_img_directory_path, height_field='image_height', width_field='image_width', blank=True
    )
    thumbnail_width = PositiveIntegerField(editable=False, default=120)
    thumbnail_height = PositiveIntegerField(editable=False, default=120)
    thumbnail = ImageField(
        upload_to=user_img_directory_path, height_field='thumbnail_height', width_field='thumbnail_width', blank=True
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
        image = ContentFile(image_data.content)
        if not self.image:
            self.image.save('profile.jpg', image)
        if not self.thumbnail:
            self.image.open()
            image = Image.open(self.image)
            side_length = min([self.image_width, self.image_height])
            croped = image.crop((0, 0, side_length, side_length))
            image_io = BytesIO()
            croped.save(image_io, 'JPEG')
            self.thumbnail.save('thumbnail.jpg', ContentFile(image_io.getvalue()))

    def update_profile(self):
        if self.social_account and self.social_account.provider == 'facebook' and not (self.image and self.thumbnail):
            self.update_image_by_facebook()
