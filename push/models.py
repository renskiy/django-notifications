from enum import Enum

from django.apps import apps
from django.conf import settings as django_settings
from django.db import models

from push import settings


class DeviceOS(Enum):

    iOS = 1
    Android = 2


class DeviceBase(models.Model):

    class Meta:
        unique_together = ['device_os', 'push_token']
        abstract = True

    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices', related_query_name='device')
    device_locale = models.CharField(max_length=255, blank=True)
    device_os = models.SmallIntegerField(choices=(
        (DeviceOS.iOS.value, DeviceOS.iOS.name),
        (DeviceOS.Android.value, DeviceOS.Android.name)
    ))
    push_token = models.CharField(max_length=255, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)


class Device(DeviceBase):

    class Meta:
        swappable = 'PUSH_DEVICE_MODEL'


def get_device_model() -> DeviceBase:
    return apps.get_model(settings.PUSH_DEVICE_MODEL)


def update_device_info(user, push_token, device_os, device_locale='', **extra):
    get_device_model().objects.update_or_create(
        push_token=push_token,
        device_os=DeviceOS(device_os).value,
        defaults=dict(
            user=user,
            device_locale=device_locale,
            **extra
        ),
    )
