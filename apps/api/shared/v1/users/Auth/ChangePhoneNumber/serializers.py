from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers


class ChangePhoneNumberSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(required=True)
    session = serializers.CharField(max_length=255, required=True)
