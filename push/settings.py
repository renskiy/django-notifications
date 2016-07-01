from django.conf import settings

PUSH_APNS = getattr(settings, 'PUSH_APNS', {})

PUSH_AMQP_CONNECTION = getattr(settings, 'PUSH_AMQP_CONNECTION', None)

PUSH_AMQP_EXCHANGE = getattr(settings, 'PUSH_AMQP_EXCHANGE', 'push.notifications')

PUSH_WORKER_WAIT_TIMEOUT = getattr(settings, 'PUSH_WORKER_WAIT_TIMEOUT', None)

PUSH_DEVICE_MODEL = getattr(settings, 'PUSH_DEVICE_MODEL', 'push.Device')
