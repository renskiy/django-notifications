import logging

import apns_clerk as apns

from django.utils.functional import cached_property
from kombu.pools import producers

from push import settings, models, amqp

apns_logger = logging.getLogger('push.apns')

gcm_logger = logging.getLogger('push.gcm')

apns_session = apns.Session()


class Notification:

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
    def device_model(self):
        return models.get_device_model()

    def delete_tokens(self, tokens):
        self.device_model.objects.filter(
            device_os=self.device_os.value,
            push_token__in=tokens,
        ).delete()

    @cached_property
    def apns(self):
        return apns.APNs(apns_session.get_connection(**settings.PUSH_APNS))

    def send(self):
        with producers[amqp.connection].acquire(block=True) as producer:
            producer.publish(
                self.to_dict(),
                exchange=amqp.exchange,
                routing_key=self.device_os.name,
                declare=[amqp.exchange, amqp.apns_queue, amqp.gcm_queue],
                serializer='json',
            )

    def send_immediately(self, retry=1):
        if self.device_os is models.DeviceOS.iOS:
            self.send_to_apns(retry=retry)
        elif self.device_os is models.DeviceOS.Android:
            self.send_to_gcm(retry=retry)

    def _apns_send_message(self, message, retry=1):
        result = self.apns.send(message)

        if result.failed:
            apns_logger.debug(
                'Some tokens (%i) failed and will be deleted',
                len(result.failed),
            )
            self.delete_tokens(result.failed.keys())

        for reason, explanation in result.errors:
            apns_logger.error('PUSH notification was not sent, reason: %s (%s)',
                              reason, explanation)

        if result.needs_retry():
            if retry <= 0:
                apns_logger.error('PUSH notification was not sent, '
                                  'reason: retry')
            else:
                apns_logger.warning(
                    'Message need to be sent again (attempts left: %i)',
                    retry,
                )
                failed_message = result.retry()
                self._apns_send_message(failed_message, retry - 1)

    def send_to_apns(self, retry=1):
        message = apns.Message(
            tokens=self.tokens,
            alert=self.alert,
            **self.extra
        )
        self._apns_send_message(message, retry=retry)

    def send_to_gcm(self, retry=1):
        pass
