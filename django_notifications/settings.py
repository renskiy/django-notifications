from django.conf import settings

DJANGO_NOTIFICATIONS_APNS = getattr(settings, 'DJANGO_NOTIFICATIONS_APNS', {})

DJANGO_NOTIFICATIONS_FCM = getattr(settings, 'DJANGO_NOTIFICATIONS_FCM', {})

DJANGO_NOTIFICATIONS_AMQP_CONNECTION = getattr(settings, 'DJANGO_NOTIFICATIONS_AMQP_CONNECTION', None)

DJANGO_NOTIFICATIONS_AMQP_EXCHANGE = getattr(settings, 'DJANGO_NOTIFICATIONS_AMQP_EXCHANGE', 'push.notifications')

DJANGO_NOTIFICATIONS_AMQP_QUEUE_PREFIX = getattr(settings, 'DJANGO_NOTIFICATIONS_AMQP_QUEUE_PREFIX', 'push.notifications.')

DJANGO_NOTIFICATIONS_WORKER_WAIT_TIMEOUT = getattr(settings, 'DJANGO_NOTIFICATIONS_WORKER_WAIT_TIMEOUT', None)

DJANGO_NOTIFICATIONS_DEVICE_MODEL = getattr(settings, 'DJANGO_NOTIFICATIONS_DEVICE_MODEL', 'push.Device')
