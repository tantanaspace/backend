from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer


class UserRegistrationAPIView(CreateAPIView):
    """
    User registration API with OTP verification
    Requires phone number to be verified with OTP first
    """
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.save()
        
        return Response({
            'user': {
                'id': user.id,
                'phone_number': str(user.phone_number),
                'full_name': user.full_name,
                'username': user.username,
                'date_of_birth': user.date_of_birth,
                'gender': user.gender,
            },
            'tokens': user.tokens
        }, status=status.HTTP_201_CREATED)
