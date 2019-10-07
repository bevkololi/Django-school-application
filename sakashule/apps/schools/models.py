import random
import string
from datetime import date
import datetime
from django.template.defaultfilters import slugify

from django.db import models
from sakashule.apps.authentication.models import User
from sakashule.apps.profiles.models import Profile
from sakashule.apps.core.models import TimestampsMixin, SoftDeleteMixin
from geoposition.fields import GeopositionField
from cloudinary.models import CloudinaryField


class School(TimestampsMixin, SoftDeleteMixin):
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    name = models.CharField(max_length=255)
    school = models.ForeignKey('authentication.User',
                               related_name='schools',
                               on_delete=models.CASCADE)
    about = models.TextField(default="Update school's description")
    history = models.TextField(default="Update school history")
    # fee_structure = models.FileField()
    # events = models.FileField(default="Update school events")
    # updates = models.FileField("Add updates")
    # uniforms = models.URLField(default='')
    # location = GeopositionField()
    # results = models.FileField()

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


class Event(TimestampsMixin):
    event_id = models.AutoField(primary_key=True)
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=255)
    date = models.DateField(default=datetime.date.today())
    time = models.TimeField()
    body = models.TextField(default="Update Event")

    class Meta:
        ordering = ['event_id']


class Update(TimestampsMixin):
    update_id = models.AutoField(primary_key=True)
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="updates")
    title = models.CharField(max_length=255)
    date = models.DateField(default=datetime.date.today())
    time = models.TimeField(default=datetime.datetime.now().time())
    body = models.TextField(default="Update Event")

    class Meta:
        ordering = ['update_id']


class Uniform(TimestampsMixin):
    uniform_id = models.AutoField(primary_key=True)
    school = models.ForeignKey(
        School, on_delete=models.CASCADE, related_name="uniforms")
    image = CloudinaryField("image")
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)

    class Meta:
        ordering = ['uniform_id']
