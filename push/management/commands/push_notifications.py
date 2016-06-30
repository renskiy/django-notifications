import logging
import socket
import time

import apns_clerk as apns
import gcm
import kombu
import kombu.message

from django.conf import settings
from django.core.management.base import BaseCommand

from push.models import Notification

logger = logging.getLogger('push_notifications')


class Command(BaseCommand):

    RETRY_SECONDS = 5

    MAX_ATTEMPTS = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apns = apns.APNs(apns.Session().get_connection(**settings.PUSH_APNS))
        # self.gcm = gcm.GCM()

    def delete_tokens(self, tokens):
        if not tokens:
            return
            # TODO

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

    def apns_send_message(self, tokens, alert=None, **meta):
        message = apns.Message(
            tokens=tokens,
            alert=alert,
            **meta,
        )
        self._apns_send_message(message)

    def gcm_send_message(self, tokens, alert=None, **meta):
        pass

    def on_notification(self, body, message: kombu.message.Message):
        logger.debug(
            'Received PUSH notification message (%i)',
            len(message.body),
        )
        try:
            notification = Notification(**body)
        except (ValueError, TypeError):
            logger.error('Skipped invalid AMQP message body: %s', body)
        else:
            try:
                notification.send_immediately()
            except Exception:
                logger.exception('Notification was not sent due to error')
        message.ack()

    def handle(self, **options):
        with kombu.Connection(settings.AMQP) as connection:
            push_notifications = kombu.Queue(name='push_notifications')  # TODO move to settings
            with connection.Consumer(
                queues=[push_notifications],
                callbacks=[self.on_notification],
            ):
                try:
                    while True:
                        connection.drain_events(
                            timeout=settings.PUSH_QUEUE_TIMEOUT,
                        )
                except socket.timeout:
                    pass
