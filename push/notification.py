import functools
import logging

import apns_clerk as apns
import kombu

from django.apps import apps
from django.conf import settings
from kombu.common import maybe_declare
from kombu.pools import producers

from push import default_settings, models

logger = logging.getLogger('push')

amqp_exchange = kombu.Exchange(
    name=getattr(
        settings,
        'PUSH_AMQP_EXCHANGE',
        default_settings.PUSH_AMQP_EXCHANGE,
    ),
    type='topic',
)

amqp_connection = kombu.Connection(getattr(
    settings,
    'PUSH_AMQP_CONNECTION',
    default_settings.PUSH_AMQP_CONNECTION,
))

apns_queue = kombu.Queue(
    'push.notifications.%s' % models.DeviceOS.iOS.name,
    exchange=amqp_exchange,
    routing_key=models.DeviceOS.iOS.name,
)

gcm_queue = kombu.Queue(
    'push.notifications.%s' % models.DeviceOS.Android.name,
    exchange=amqp_exchange,
    routing_key=models.DeviceOS.Android.name,
)

apns_session = apns.Session()


@functools.lru_cache(maxsize=1)
def declare_all():
    with amqp_connection.channel() as channel:
        maybe_declare(amqp_exchange, channel)
        maybe_declare(apns_queue, channel)
        maybe_declare(gcm_queue, channel)


class Notification:

    MAX_ATTEMPTS = 3

    def __init__(self, *, tokens, device_os, alert=None, **extra):
        self.tokens = tokens
        self.device_os = models.DeviceOS(device_os)
        self.alert = alert
        self.extra = extra

    def to_dict(self):
        return dict(
            tokens=self.tokens,
            device_os=self.device_os.value,
            alert=self.alert,
            extra=self.extra,
        )

    @property
    def device_model(self) -> models.Device:
        return apps.get_model(getattr(
            settings,
            'PUSH_DEVICE_MODEL',
            default_settings.PUSH_DEVICE_MODEL,
        ))

    def delete_tokens(self, tokens):
        self.device_model.objects.filter(
            device_os=self.device_os.value,
            push_token__in=tokens,
        ).delete()

    @property
    def apns(self):
        return apns.APNs(apns_session.get_connection(
            **getattr(settings, 'PUSH_APNS', default_settings.PUSH_APNS)
        ))

    def send(self):
        declare_all()
        with producers[amqp_connection].acquire(block=True) as producer:
            producer.publish(
                self.to_dict(),
                exchange=amqp_exchange,
                routing_key=self.device_os.name,
                serializer='json',
            )

    def send_immediately(self):
        if self.device_os is models.DeviceOS.iOS:
            self.send_to_apns()
        elif self.device_os is models.DeviceOS.Android:
            self.send_to_gcm()

    def _apns_send_message(self, message, attempt=1):
        result = self.apns.send(message)

        if result.failed:
            logger.debug(
                'Some tokens (%i) failed and will be deleted',
                len(result.failed),
            )
            self.delete_tokens(result.failed.keys())

        for reason, explanation in result.errors:
            logger.error('%s: %s', reason, explanation)

        if result.needs_retry():
            if attempt > self.MAX_ATTEMPTS:
                logger.error(
                    'MAX_ATTEMPTS=%i exceeded when trying to '
                    'send PUSH notification',
                    self.MAX_ATTEMPTS,
                )
            else:
                failed_message = result.retry()
                logger.warning(
                    'Message need to be sent again (attempt #%i)',
                    attempt,
                )
                self._apns_send_message(failed_message, attempt + 1)

    def send_to_apns(self):
        message = apns.Message(
            tokens=self.tokens,
            alert=self.alert,
            **self.extra
        )
        self._apns_send_message(message)

    def send_to_gcm(self):
        pass
