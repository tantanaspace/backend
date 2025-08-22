from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from django.contrib.auth import get_user_model

class UserInfoUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = get_user_model()
        fields = (
            'first_name',
            'last_name',
            'phone_number',
            'avatar',
            'password',
        )
    
    def validate_password(self, value):
        """
        Checks that the password meets standard security requirements.
        """
        try:
            password_validation.validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return value
    
    def update(self, instance, validated_data):
        # Handle password update separately
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance