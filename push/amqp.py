import kombu

from django.conf import settings

from push import default_settings, models

exchange = kombu.Exchange(
    name=getattr(
        settings,
        'PUSH_AMQP_EXCHANGE',
        default_settings.PUSH_AMQP_EXCHANGE,
    ),
    type='topic',
)

connection = kombu.Connection(getattr(
    settings,
    'PUSH_AMQP_CONNECTION',
    default_settings.PUSH_AMQP_CONNECTION,
))

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
