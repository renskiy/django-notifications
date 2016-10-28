from distutils.core import setup
from setuptools import find_packages

with open('README.rst') as description:
    long_description = description.read()

setup(
    name='django-push-service',
    version='0.1',
    author='Rinat Khabibiev',
    author_email='srenskiy@gmail.com',
    packages=list(map('django_push.'.__add__, find_packages('django_push'))) + ['django_push'],
    url='https://github.com/renskiy/django-push-service',
    license='MIT',
    description='django-push-service',
    long_description=long_description,
    classifiers=[
        # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'kombu>=3.0,<4.0',
        'apns-clerk>=0.2,<0.3',
        'pyfcm>=1.1,<1.2',
    ],
)
