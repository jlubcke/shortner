from django.conf import settings
from django.contrib.auth.models import User
from django.db import models


class Entry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='entries', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    short = models.CharField(max_length=255, unique=True)
