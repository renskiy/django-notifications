import functools

import kombu

from django.conf import settings
from kombu.common import maybe_declare

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


@functools.lru_cache(maxsize=1)
def declare_all():
    with connection.channel() as channel:
        maybe_declare(exchange, channel)
        maybe_declare(apns_queue, channel)
        maybe_declare(gcm_queue, channel)
