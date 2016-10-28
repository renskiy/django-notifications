from distutils.core import setup
from setuptools import find_packages

with open('README.rst') as description:
    long_description = description.read()

setup(
    name='django-push',
    version='0.1',
    author='Rinat Khabibiev',
    author_email='srenskiy@gmail.com',
    packages=list(map('push.'.__add__, find_packages('push'))) + ['push'],
    url='https://github.com/renskiy/django-push',
    license='MIT',
    description='fabricio',
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'License :: OSI Approved :: MIT License',
        'Framework :: Django :: 1.9',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'kombu>=3.0,<4.0',
        'apns-clerk>=0.2,<0.3',
        'pyfcm>=1.1,<1.2',
    ],
)
