from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class PhoneNumberBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate
    using their phone number instead of username.
    """
    
    def authenticate(self, request, phone_number=None, password=None, **kwargs):
        if phone_number is None or password is None:
            return None
        
        try:
            # Try to fetch the user by phone number
            user = User.objects.get(phone_number=phone_number)
        except User.DoesNotExist:
            return None
        
        # Check if the user has a usable password
        if not user.has_usable_password():
            return None
        
        # Check if the provided password is correct
        if user.check_password(password):
            return user
        
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 