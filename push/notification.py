import logging

import apns_clerk as apns

from django.conf import settings

from push import default_settings
from push.models import DeviceOS

logger = logging.getLogger('push.notification')

apns_session = apns.Session()


class Notification:

    def __init__(self, *, tokens, device_os, alert=None, **extra):
        self.tokens = tokens
        self.device_os = DeviceOS(device_os)
        self.alert = alert
        self.extra = extra

    @property
    def apns(self):
        return apns.APNs(apns_session.get_connection(
            **getattr(settings, 'PUSH_APNS', default_settings.PUSH_APNS)
        ))

    def send(self):
        pass
        # TODO enqueue

    def send_immediately(self):
        if self.device_os is DeviceOS.iOS:
            self._send_to_apns()
        elif self.device_os is DeviceOS.Android:
            self._send_to_gcm()

    def _apns_send_message(self, message, attempt=1):
        result = self.apns.send(message)

        failed_tokens = []
        for token, (reason, explanation) in result.failed.items():
            logger.debug('Failed token %s, %s: %s', token, reason, explanation)
            failed_tokens.append(token)
        self.delete_tokens(failed_tokens)

        for reason, explanation in result.errors:
            logger.error('%s: %s', reason, explanation)

        if result.needs_retry():
            if attempt > self.MAX_ATTEMPTS:
                logger.error(
                    'MAX_ATTEMPTS=%i exceeded when trying to '
                    'send PUSH notification',
                    self.MAX_ATTEMPTS,
                )
            failed_message = result.retry()
            logger.warning(
                'Message need to be sent again (attempt #%i), '
                'waiting for %i seconds before next attempt...',
                attempt,
                self.RETRY_SECONDS * attempt,
                )
            time.sleep(self.RETRY_SECONDS * attempt)
            self._apns_send_message(failed_message, attempt + 1)

    def _send_to_apns(self):
        message = apns.Message(
            tokens=self.tokens,
            alert=self.alert,
            **self.extra,
        )
        self._apns_send_message(message)

    def _send_to_gcm(self):
        pass
