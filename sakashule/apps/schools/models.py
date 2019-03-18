import random
import string
from django.template.defaultfilters import slugify

from django.db import models
from sakashule.apps.authentication.models import User
from sakashule.apps.profiles.models import Profile
from sakashule.apps.core.models import TimestampsMixin, SoftDeleteMixin
from geoposition.fields import GeopositionField


class School(TimestampsMixin, SoftDeleteMixin):
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    school = models.ForeignKey('authentication.User',
                              related_name='schools',
                              on_delete=models.CASCADE)
    about = models.CharField(max_length=400, default="Description")
    history = models.TextField(default="Update school history")
    fee_structure = models.FileField(default="Update school fee structure")
    events = models.FileField(default="Update school events")
    updates = models.FileField("Add updates")
    uniforms = models.URLField(default='')
    location = GeopositionField(default='')
    results = models.FileField(default='')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(School, self).save(*args, **kwargs)


class Comment(TimestampsMixin):
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    author = models.ForeignKey(
        'profiles.Profile', related_name="comments", blank=True, on_delete=models.CASCADE)
