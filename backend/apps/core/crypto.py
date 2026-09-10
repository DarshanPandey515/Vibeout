from cryptography.fernet import Fernet

from django.conf import settings


def _fernet():
    return Fernet(settings.CREDENTIAL_ENCRYPTION_KEY.encode())


def encrypt(value):
    return _fernet().encrypt(value.encode())


def decrypt(value):
    return _fernet().decrypt(bytes(value)).decode()
