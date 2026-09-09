import os

from pathlib import Path

from dotenv import load_dotenv
from twilio.rest import Client


load_dotenv(Path(__file__).resolve().parents[1] / ".env")

account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

client = Client(account_sid, auth_token)

call = client.calls.create(
    twiml="<Response><Say>Hello Prince bro</Say></Response>",
    to="+919731142571",
    from_="+12294583181",
)

print(call.sid)