import hashlib
import hmac
import json
import urllib.parse

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class TelegramWebAppAuthentication(BaseAuthentication):
    """
    Authentication through Telegram WebApp initData.
    Expects header: Authorization: Telegram <initData>
    """

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Telegram "):
            return None  # Not our type of authentication

        init_data = auth_header.replace("Telegram ", "", 1).strip()
        parsed_data = self._verify_init_data(init_data)
        if not parsed_data:
            raise AuthenticationFailed("Invalid Telegram initData signature")

        # user JSON
        user_json = urllib.parse.unquote(parsed_data.get("user", ""))
        if not user_json:
            raise AuthenticationFailed("No user data in initData")

        try:
            user_data = json.loads(user_json)
        except json.JSONDecodeError:
            raise AuthenticationFailed("Invalid user JSON in initData")

        telegram_id = str(user_data.get("id"))
        if not telegram_id:
            raise AuthenticationFailed("Telegram user ID missing")

        try:
            user = User.objects.get(telegram_id=telegram_id)
        except User.DoesNotExist:
            raise AuthenticationFailed("User with this Telegram ID not found")

        return user, None

    def _verify_init_data(self, init_data: str) -> dict | None:
        parsed_data = dict(urllib.parse.parse_qsl(init_data))
        hash_received = parsed_data.pop("hash", None)
        if not hash_received:
            return None

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )
        secret_key = hmac.new(
            b"WebAppData", settings.TELEGRAM_BOT["token"].encode(), hashlib.sha256
        ).digest()
        hash_calculated = hmac.new(
            secret_key, data_check_string.encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(hash_calculated, hash_received):
            return None

        return parsed_data
