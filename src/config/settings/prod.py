from .base import *

#this file is unversionned and contains secrets such SECRET_KEY or database credentials
import config.settings.secrets as secrets

SECRET_KEY = secrets.SECRET_KEY
ALLOWED_HOSTS = secrets.ALLOWED_HOSTS
