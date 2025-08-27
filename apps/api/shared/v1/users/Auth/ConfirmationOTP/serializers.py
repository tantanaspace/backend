from enum import Enum

from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


class UserAction(str, Enum):
    """User action type based on phone number status"""
    REGISTRATION = 'registration'
    FORGOT_PASSWORD = 'forgot-password'
    CHANGE_PHONE_NUMBER = 'change-phone-number'


class ConfirmationOTPSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    session = serializers.CharField(max_length=255, required=True)
    otp_code = serializers.CharField(max_length=6, required=True)
    action = serializers.ChoiceField(choices=UserAction, required=True)