from django.urls import path
from .api_endpoints import *

urlpatterns = [
    path("send-otp/", SendSMSView.as_view(), name="send-otp"),
    path("verify-otp/", CheckOTPView.as_view(), name="verify-otp"),
    path("login/", LoginAPIView.as_view(), name="simple-login"),
    path("check-user/", UserExistsAPIView.as_view(), name="check-user"),
    path("register/", UserRegistrationAPIView.as_view(), name="user-registration"),
    path("forgot-password/", ResetPasswordView.as_view(), name="forgot-password-reset"),
]
