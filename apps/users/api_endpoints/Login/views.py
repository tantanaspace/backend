from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404

from .serializers import LoginSerializer, UserExistsSerializer
from apps.users.models import User


class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        return Response(user.tokens, status=status.HTTP_200_OK)


class UserExistsAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserExistsSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        user_exists = User.objects.filter(phone_number=phone_number).exists()

        return Response({
            'exists': user_exists,
            'phone_number': phone_number
        }, status=status.HTTP_200_OK)
