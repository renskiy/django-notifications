import logging

import apns_clerk as apns
import pyfcm as fcm

from django.utils.functional import cached_property
from kombu.pools import producers

from push import settings, models, amqp

apns_logger = logging.getLogger('push.notifications.apns')

fcm_logger = logging.getLogger('push.notifications.fcm')


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
            **self.extra,
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
    def apns_session(self):
        return apns.Session()

    @property
    def apns(self):
        return apns.APNs(self.apns_session.get_connection(**settings.PUSH_APNS))

    @cached_property
    def fcm(self):
        return fcm.FCMNotification(**settings.PUSH_FCM)

    def send(self):
        with producers[amqp.connection].acquire(block=True) as producer:
            producer.publish(
                self.to_dict(),
                exchange=amqp.exchange,
                routing_key=self.device_os.name,
                declare=[amqp.exchange, amqp.apns_queue, amqp.fcm_queue],
                serializer='json',
            )

    def send_immediately(self, retry=1):
        if self.device_os is models.DeviceOS.iOS:
            self.send_to_apns(retry=retry)
        elif self.device_os is models.DeviceOS.Android:
            self.send_to_fcm(retry=retry)

    def _apns_send_message(self, message, retry=1):
        result = self.apns.send(message)

        if result.failed:
            apns_logger.debug(
                'Some tokens (%i) failed and will be deleted',
                len(result.failed),
            )
            self.delete_tokens(result.failed.keys())

        for reason, explanation in result.errors:
            apns_logger.error(
                'PUSH notification was not sent, reason: %s (%s)',
                reason,
                explanation
            )

        if result.needs_retry():
            if retry <= 0:
                apns_logger.error(
                    'PUSH notification was not sent, reason: retry'
                )
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

    def send_to_fcm(self, retry=1):

        operation_responses = self.fcm.notify_multiple_devices(
            registration_ids=self.tokens,
            message_body=self.alert,
            **self.extra
        )

        for operation_response in operation_responses:
            notification_result = operation_response.get('results', dict())
            error = notification_result.get('error')
            if error:
                fcm_logger.error(
                    'PUSH notification was not sent, reason: %s',
                    error,
                )
