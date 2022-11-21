import os

from coolpress.coolpress.settings import *

DEBUG = False
ALLOWED_HOSTS = ['*']

SECRET_KEY = os.environ['DJANGO_SECRET_KEY']