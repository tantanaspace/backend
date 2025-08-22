from django.contrib.auth import get_user_model
from rest_framework import serializers


class ForgotPasswordSendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    return_url = serializers.URLField()
    role = serializers.ChoiceField(choices=get_user_model().Role.choices)
