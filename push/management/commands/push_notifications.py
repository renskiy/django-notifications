import logging
import socket

import kombu
import kombu.message

from django.conf import settings
from django.core.management.base import BaseCommand

from push import default_settings
from push.notification import Notification, apns_queue, gcm_queue, amqp_connection

logger = logging.getLogger('push')


class Command(BaseCommand):

    @staticmethod
    def on_notification(body, message: kombu.message.Message):
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
            except:
                logger.exception('Notification was not sent due to error')
        message.ack()

    def handle(self, **options):
        # notification = Notification(
        #     tokens='tokens',
        #     device_os=DeviceOS.iOS,
        # )
        # notification.send()
        logger.debug('Started listening PUSH notifications queue')
        with amqp_connection as connection:
            with connection.Consumer(
                queues=[apns_queue, gcm_queue],
                callbacks=[self.on_notification],
            ):
                try:
                    while True:
                        connection.drain_events(timeout=getattr(
                            settings,
                            'PUSH_WORKER_WAIT_TIMEOUT',
                            default_settings.PUSH_WORKER_WAIT_TIMEOUT,
                        ))
                except socket.timeout:
                    pass
