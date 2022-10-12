import os

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from django.conf import settings
client = Client(os.environ["TWILIO_ACCOUNT_SID"], os.environ["TWILIO_AUTH_TOKEN"])
verify = client.verify.services(os.environ["TWILIO_VERIFY_SERVICE_SID"])


def send(phone):
    phone = "+91" + str(phone)
    verify.verifications.create(to=phone, channel="sms")


def check(phone, code):
    phone = "+91" + str(phone)
    try:
        result = verify.verification_checks.create(to=phone, code=code)

    except TwilioRestException:
        print("no")
        return False
    return result.status == "approved"
