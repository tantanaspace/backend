from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from django.contrib.auth import get_user_model

class LoginUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "phone_number",
            "full_name",
            "date_of_birth",
            "role",
            "gender",
            "language",
            "avatar",
            "date_joined",
            "is_notification_enabled",
            )
    
    

class LoginSerializer(serializers.Serializer):
    phone_number = PhoneNumberField(write_only=True, required=True)
    password = serializers.CharField(required=True, write_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user = LoginUserInfoSerializer(read_only=True)
