from django.conf import settings
from django.db import models


class Entry(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='entries', on_delete=models.CASCADE)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='approvals', on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    short = models.CharField(max_length=255, unique=True)
    use_count = models.IntegerField(default=0)
