from enum import Enum

from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


class UserAction(str, Enum):
    """User action type based on phone number status"""

    LOGIN = "login"
    REGISTRATION = "registration"
    FORGOT_PASSWORD = "forgot-password"
    CHANGE_PHONE_NUMBER = "change-phone-number"


class RequestOTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    action = serializers.ChoiceField(choices=UserAction, required=True)
