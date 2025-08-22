import base64
from urllib.parse import urlencode, urlparse, parse_qs, urlunparse

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, Throttled
from rest_framework.permissions import AllowAny

from apps.api.shared.v1.users.Auth.ForgotPasswordSendEmail.serializers import ForgotPasswordSendEmailSerializer
from apps.users.tasks import send_html_email
from utils.generators import *


class ForgotPasswordSendEmailAPIView(GenericAPIView):
    serializer_class = ForgotPasswordSendEmailSerializer
    permission_classes = (AllowAny,)
    
    # Configuration for expiration times (in minutes)
    CODE_EXPIRATION_TIME = 5

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        return_url = serializer.validated_data['return_url']
        role = serializer.validated_data['role']

        try:
            user = get_user_model().objects.get(email=email, role=role)
        except get_user_model().DoesNotExist:
            raise NotFound(_("User with this email does not exist."), code='not_found')

        cooldown_key = generate_cache_key(CacheType.FORGOT_PASSWORD, email)
        # if cache.keys(f'{cooldown_key}*'):
        #     raise Throttled(detail=_("You can request a new link only once {} minute.").format(self.CODE_EXPIRATION_TIME))

        session = generate_code(length=32, code_type=CodeType.NON_STANDARD)
        base_64_session = base64.b64encode(session.encode()).decode()
        base_64_email = base64.b64encode(email.encode()).decode()
        cache_key = generate_cache_key(CacheType.FORGOT_PASSWORD, email, session)
        cache.set(cache_key, user.pk, timeout=self.CODE_EXPIRATION_TIME * 60)

        # Build the reset URL using urllib.parse
        reset_url = self._build_reset_url(return_url, base_64_session, base_64_email)
        
        send_html_email.delay(
            subject="🔐 Reset Password",
            to_email=email,
            template_name="emails/reset_password.html",
            context={
                "expiration_time": self.CODE_EXPIRATION_TIME,
                "url": reset_url,
                "role": user.role
            }
        )

        return Response({
            "email": email,
            "role": user.role,
            "expiration_time": self.CODE_EXPIRATION_TIME
        }, status=200)

    def _build_reset_url(self, base_url: str, session: str, email: str) -> str:
        """
        Build reset URL using standard urllib.parse functions.
        """
        parsed = urlparse(base_url)
        params = parse_qs(parsed.query)
        params['session'] = [session]
        params['email'] = [email]

        new_query = urlencode(params, doseq=True)
        return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, new_query, parsed.fragment))


__all__ = [
    'ForgotPasswordSendEmailAPIView'
]
