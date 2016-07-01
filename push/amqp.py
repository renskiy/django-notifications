import kombu

from push import settings, models

exchange = kombu.Exchange(
    name=settings.PUSH_AMQP_EXCHANGE,
    type='topic',
)

connection = kombu.Connection(settings.PUSH_AMQP_CONNECTION)

apns_queue = kombu.Queue(
    'push.notifications.%s' % models.DeviceOS.iOS.name,
    exchange=exchange,
    routing_key=models.DeviceOS.iOS.name,
)

gcm_queue = kombu.Queue(
    'push.notifications.%s' % models.DeviceOS.Android.name,
    exchange=exchange,
    routing_key=models.DeviceOS.Android.name,
)
