from django.contrib.auth import get_user_model
from rest_framework import serializers



class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'email',
            'avatar',
            'first_name',
            'last_name',
            'phone_number',
            'role',
            'language',
            'date_joined'
        )
        read_only_fields = fields 