from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from apps.core.crypto import decrypt


def client_for(account):
    if account.api_key_sid and account.api_key_secret_encrypted:
        return Client(
            account.api_key_sid,
            decrypt(account.api_key_secret_encrypted),
            account_sid=account.twilio_account_sid,
        )
    return Client(account.twilio_account_sid, decrypt(account.auth_token_encrypted))


def verify_credentials(account_sid, auth_token):
    Client(account_sid, auth_token).api.accounts(account_sid).fetch()


def list_incoming_numbers(account):
    return client_for(account).incoming_phone_numbers.list()


def configure_voice_webhook(account, twilio_sid, url):
    client_for(account).incoming_phone_numbers(twilio_sid).update(voice_url=url)


def place_call(account, to, from_, url, status_callback):
    return client_for(account).calls.create(
        to=to, from_=from_, url=url, status_callback=status_callback
    )


__all__ = [
    "TwilioRestException",
    "client_for",
    "verify_credentials",
    "list_incoming_numbers",
    "configure_voice_webhook",
    "place_call",
]
