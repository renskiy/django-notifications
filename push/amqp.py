import kombu

from push import settings, models

exchange = kombu.Exchange(
    name=settings.PUSH_AMQP_EXCHANGE,
    type='topic',
)

connection = kombu.Connection(settings.PUSH_AMQP_CONNECTION)

apns_queue = kombu.Queue(
    settings.PUSH_AMQP_QUEUE_PREFIX + models.DeviceOS.iOS.name,
    exchange=exchange,
    routing_key=models.DeviceOS.iOS.name,
)

gcm_queue = kombu.Queue(
    settings.PUSH_AMQP_QUEUE_PREFIX + models.DeviceOS.Android.name,
    exchange=exchange,
    routing_key=models.DeviceOS.Android.name,
)
