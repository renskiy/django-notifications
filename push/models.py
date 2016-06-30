from enum import Enum

from django.conf import settings
from django.db import models


class DeviceOS(Enum):

    iOS = 1
    Android = 2


class DeviceBase(models.Model):

    class Meta:
        unique_together = ['device_os', 'push_token']
        abstract = True

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices', related_query_name='device')
    device_id = models.CharField(max_length=255, blank=True)
    device_locale = models.CharField(max_length=255, blank=True)
    device_os = models.SmallIntegerField(choices=(
        (DeviceOS.iOS.value, DeviceOS.iOS.name),
        (DeviceOS.Android.value, DeviceOS.Android.name)
    ))
    device_os_version = models.CharField(max_length=255, blank=True)
    push_token = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class Device(DeviceBase):

    class Meta:
        swappable = 'PUSH_DEVICE_MODEL'
