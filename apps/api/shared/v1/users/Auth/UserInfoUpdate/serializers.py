from rest_framework import serializers
from django.contrib.auth import get_user_model

class UserInfoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'full_name',
            'date_of_birth',
            'gender',
            'avatar',
        )