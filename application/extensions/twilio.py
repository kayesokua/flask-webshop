import logging
import os
import random
import time
from datetime import datetime
import hmac
import pytz

from flask import flash
from twilio.rest import Client

from application import db

logger = logging.getLogger(__name__)

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
service_sid = os.environ.get('TWILIO_SERVICE')

client = Client(account_sid, auth_token)

def generate_custom_code():
    num1 = random.randint(1, 9)
    num2 = random.randint(0, 9)
    num3 = random.randint(0, 9)
    num4 = random.randint(0, 9)
    num5 = random.randint(0, 9)
    num6 = random.randint(0, 9)
    custom_code = str(num1) + str(num2) + str(num3) + str(num4) + str(num5) + str(num6)
    return custom_code

def send_verification(mobile, current_user):
    if current_user.last_mobile_code_sent is None or current_user.last_mobile_code_sent.date() != datetime.now().date():
        print(mobile)
        custom_code = generate_custom_code()
        custom_message = f"Flask Webshop: Your verification code is {custom_code}."
        message = client.messages.create(
            body=custom_message,
            to=mobile,
            from_='+14407501083')
        if message:
            current_user.twilio_sid = message.sid
            current_user.mobile_code = custom_code
            current_user.mobile_verification_error = 0
            current_user.last_mobile_code_sent = datetime.utcnow()
            db.session.commit()
            return True
    else:
        logger.error(f"Failed to send verification to {mobile}")
        flash("Failed to send verification code. Please try again later.")
    return False

def check_verification_token(token, current_user):

    if current_user.mobile_verification_error >= 3:
        flash("You have exceeded the maximum number of attempts. Please try again tomorrow.")
        return False

    if token != current_user.mobile_code:
        current_user.mobile_verification_error += 1
        db.session.commit()
        return False

    now = datetime.now(pytz.utc)
    if current_user.last_mobile_code_sent.date() != now.date():
        flash("Verification code has expired. Please request a new one.")
        return False

    current_user.mobile_verification_error = 0
    current_user.is_mobile_verified = True
    current_user.last_mobile_verified = datetime.utcnow()
    db.session.commit()

    return True

def send_checkout_verification(mobile, order):
    custom_code = generate_custom_code()
    custom_message = f"Please confirm your purchase of {order.grand_total} using this {custom_code}."
    message = client.messages.create(
        body=custom_message,
        to='+491635142007',
        from_='+14407501083')
    order.checkout_verification_code = custom_code
    db.session.commit()

def check_checkout_verification(token, order):
    if token == order.checkout_verification_code:
        order.is_checkout_verified = True
        db.session.commit()
        return True
    else:
        return False