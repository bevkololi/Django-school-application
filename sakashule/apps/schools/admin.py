from django.contrib import admin

from sakashule.apps.schools.models import School, Comment

admin.site.register(Comment)
admin.site.register(School)