from django.conf import settings
from django.core import signing


def mint_call_token(call_id):
    return signing.dumps(
        {"call_id": str(call_id)},
        key=settings.INTERNAL_SIGNING_KEY,
        salt="internal-call",
    )


def verify_call_token(token, call_id):
    try:
        payload = signing.loads(
            token,
            key=settings.INTERNAL_SIGNING_KEY,
            salt="internal-call",
            max_age=3600,
        )
    except Exception:
        return False
    return payload.get("call_id") == str(call_id)