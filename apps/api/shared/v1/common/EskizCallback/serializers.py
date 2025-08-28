from rest_framework import serializers


class EskizCallbackSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=255)
    request_id = serializers.CharField(max_length=255)
