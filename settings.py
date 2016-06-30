import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'secret_key'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'push',
]

MIDDLEWARE_CLASSES = []


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

TIME_ZONE = 'UTC'

USE_TZ = True


# Push settings

PUSH_AMQP_CONNECTION = 'pyamqp://rabbitmq:rabbitmq@localhost:5672//'

PUSH_APNS = dict(
    address='push_sandbox',
    cert_file=os.path.join(BASE_DIR, 'etc/cert/apns/pins.pem'),
    passphrase='pins',
)

PUSH_WORKER_WAIT_TIMEOUT = 60
