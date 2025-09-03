from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from fcm_django.api.rest_framework import FCMDeviceAuthorizedViewSet as FCMViewSet


from apps.api.shared.v1.common import (
    ConfigDetailAPIView,
    EskizCallbackAPIView,
)

from apps.api.shared.v1.common.Options import (
    RegionOptionListAPIView,
    CountryOptionListAPIView,
    FacilityListAPIView,
    TagListAPIView,
    VenueCategoryListAPIView,
)

from apps.api.shared.v1.users.Auth import (
    ChangePhoneNumberAPIView,
    ConfirmationOTPAPIView,
    LoginAPIView,
    TelegramLoginAPIView,
    RegistrationAPIView,
    RequestOTPAPIView,
    ResetPasswordAPIView,
    UserInfoAPIView,
    UserInfoUpdateAPIView,
    DeleteAccountAPIView,
)

from apps.api.shared.v1.notifications import (
    UserNotificationListAPIView,
    UserNotificationReadAPIView,
    UserNotificationReadAllView,
)

app_name = 'shared_v1'

urlpatterns = [
    # users.auth
    path('auth/login/', LoginAPIView.as_view(), name='login'),
    path('auth/telegram-login/', TelegramLoginAPIView.as_view(), name='telegram_login'),
    path('auth/request-otp/', RequestOTPAPIView.as_view(), name='request_otp'),
    path('auth/confirmation-otp/', ConfirmationOTPAPIView.as_view(), name='confirmation_otp'),
    
    path('auth/registration/', RegistrationAPIView.as_view(), name='registration'),
    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='reset_password'),
    path('auth/change-phone-number/', ChangePhoneNumberAPIView.as_view(), name='change_phone_number'),
    
    path('auth/user-info/', UserInfoAPIView.as_view(), name='user_info'),
    path('auth/user-info-update/', UserInfoUpdateAPIView.as_view(), name='user_info_update'),
    
    path('auth/delete-account/', DeleteAccountAPIView.as_view(), name='delete_account'),
    
    path("auth/token-refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    
    # notifications
    path('notification-list/', UserNotificationListAPIView.as_view(), name='notification-list'),
    path('notification-read/<int:pk>/', UserNotificationReadAPIView.as_view(), name='notification-detail'),
    path('notification-read-all/', UserNotificationReadAllView.as_view(), name='notification-read-all'),
    path('create-device/', FCMViewSet.as_view({'post': 'create'}), name='create_fcm_device'),
    path('delete-device/<str:registration_id>/', FCMViewSet.as_view({'delete': 'destroy'}), name='delete_fcm_device'),
    path('update-device/<str:registration_id>/', FCMViewSet.as_view({'patch': 'partial_update'}), name='update_fcm_device'),

    # common.options
    path('options/regions/', RegionOptionListAPIView.as_view(), name='region-option-list'),
    path('options/countries/', CountryOptionListAPIView.as_view(), name='country-option-list'),
    path('options/facilities/', FacilityListAPIView.as_view(), name='facility-option-list'),
    path('options/tags/', TagListAPIView.as_view(), name='tag-option-list'),
    path('options/venue-categories/', VenueCategoryListAPIView.as_view(), name='venue-category-option-list'),

    # common
    path('config/', ConfigDetailAPIView.as_view(), name='config-detail'),
    path('eskiz-callback/', EskizCallbackAPIView.as_view(), name='eskiz-callback'),
]
