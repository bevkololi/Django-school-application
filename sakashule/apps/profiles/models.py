from django.db import models

from sakashule.apps.core.models import TimestampsMixin
from sakashule.settings import AUTH_USER_MODEL
from cloudinary.models import CloudinaryField


class Profile(TimestampsMixin):
    user = models.OneToOneField(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    county = models.TextField(default="What county are you situated in?")
    level = models.TextField(default="Kindly indicate what level the school is (Primary, Highschool or University).")
    ownership = models.TextField(default="Kindly update if Private or Public")
    bio = models.TextField(default="Update your bio")
    image = CloudinaryField("image")


    @property
    def username(self):
        return self.user.username

    def __str__(self):
        return self.user.username