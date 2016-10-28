from django.conf import settings

DJANGO_PUSH_APNS = getattr(settings, 'DJANGO_PUSH_APNS', {})

DJANGO_PUSH_FCM = getattr(settings, 'DJANGO_PUSH_FCM', {})

DJANGO_PUSH_AMQP_CONNECTION = getattr(settings, 'DJANGO_PUSH_AMQP_CONNECTION', None)

DJANGO_PUSH_AMQP_EXCHANGE = getattr(settings, 'DJANGO_PUSH_AMQP_EXCHANGE', 'push.notifications')

DJANGO_PUSH_AMQP_QUEUE_PREFIX = getattr(settings, 'DJANGO_PUSH_AMQP_QUEUE_PREFIX', 'push.notifications.')

DJANGO_PUSH_WORKER_WAIT_TIMEOUT = getattr(settings, 'DJANGO_PUSH_WORKER_WAIT_TIMEOUT', None)

DJANGO_PUSH_DEVICE_MODEL = getattr(settings, 'DJANGO_PUSH_DEVICE_MODEL', 'push.Device')
