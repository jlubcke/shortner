from django.conf import settings
from django.db import models


class Entry(models.Model):
    short = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='entries', on_delete=models.CASCADE)
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='approvals', on_delete=models.CASCADE, null=True)
    use_count = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = 'entries'

    def get_absolute_url(self):
        return f'/entries/{self.short}/'
