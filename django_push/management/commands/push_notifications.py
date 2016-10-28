import logging
import socket

import kombu
import kombu.message

from django.core.management.base import BaseCommand

from django_push import settings, amqp, notification

logger = logging.getLogger('django_push')


class Command(BaseCommand):

    @staticmethod
    def on_notification(body, message: kombu.message.Message):
        logger.debug(
            'Received PUSH notification message (%i)',
            len(message.body),
        )
        try:
            push_notification = notification.PushNotification(**body)
        except (ValueError, TypeError):
            logger.error('Skipped invalid AMQP message body: %s', body)
        else:
            try:
                push_notification.send_immediately()
            finally:
                message.ack()

    def handle(self, **options):

        logger.debug('Started listening PUSH notifications queues')
        with amqp.connection as connection:
            with connection.Consumer(
                queues=[amqp.apns_queue, amqp.fcm_queue],
                callbacks=[self.on_notification],
            ):
                try:
                    while True:
                        connection.drain_events(
                            timeout=settings.DJANGO_PUSH_WORKER_WAIT_TIMEOUT,
                        )
                except (socket.timeout, KeyboardInterrupt):
                    pass
