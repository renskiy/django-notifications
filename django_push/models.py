from enum import Enum

from django.apps import apps
from django.conf import settings as django_settings
from django.db import models

from django_push import settings


class DeviceOS(Enum):

    iOS = 1
    Android = 2


class DeviceBase(models.Model):

    class Meta:
        unique_together = ['device_os', 'push_token']
        abstract = True

    user = models.ForeignKey(django_settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices', related_query_name='device', null=True)
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
        swappable = 'DJANGO_PUSH_DEVICE_MODEL'


def get_device_model() -> DeviceBase:
    return apps.get_model(settings.DJANGO_PUSH_DEVICE_MODEL)


def update_push_token(push_token, device_os, user=None, device_locale='', **extra):
    if not push_token:
        return
    get_device_model().objects.update_or_create(
        push_token=push_token,
        device_os=DeviceOS(device_os).value,
        defaults=dict(
            user=user,
            device_locale=device_locale,
            **extra
        ),
    )


def delete_push_token(push_token, device_os):
    get_device_model().objects.filter(
        push_token=push_token,
        device_os=DeviceOS(device_os).value,
    ).delete()
