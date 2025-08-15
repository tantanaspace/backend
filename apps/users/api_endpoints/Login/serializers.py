from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.users.services.validators import validate_international_phonenumber
from django.utils.translation import gettext_lazy as _


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        validators=[validate_international_phonenumber]
    )
    password = serializers.CharField(
        max_length=128,
        required=True,
        write_only=True
    )

    def validate(self, data):
        phone_number = data.get('phone_number')
        password = data.get('password')

        if phone_number and password:
            user = authenticate(
                phone_number=phone_number,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    _('Invalid phone number or password.')
                )

            data['user'] = user
        else:
            raise serializers.ValidationError(
                _('Must include "phone_number" and "password".')
            )

        return data


class UserExistsSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=15,
        required=True,
        validators=[validate_international_phonenumber]
    )
