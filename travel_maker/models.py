from django.contrib.contenttypes.models import ContentType
from django.db import models
from updown.fields import RatingField
from updown.models import Vote


class TimeStamped(models.Model):
    tm_created = models.DateTimeField(auto_now_add=True)
    tm_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Votable(models.Model):
    updown = RatingField(can_change_vote=True)

    class Meta:
        abstract = True

    def get_does_user_already_vote(self, user):
        content_type = ContentType.objects.get_for_model(self.__class__)
        vote = Vote.objects.filter(user=user, object_id=self.id, content_type=content_type)
        does_user_already_vote = True if vote.exists() and vote[0].score > 0 else False

        return does_user_already_vote

    def set_does_user_already_vote(self, user):
        self.does_user_already_vote = self.get_does_user_already_vote(user)
        return self
