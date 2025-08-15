import uuid
import random
import logging
from django.core.cache import cache
from abc import ABC, abstractmethod
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.users.models import User
from apps.users.services.choices import SendOTPType

logger = logging.getLogger(__name__)


class OTPUtils:
    @staticmethod
    def generate_session() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def generate_cache_key(type: str, *args) -> str:
        return f"{type}:{':'.join(args)}"

    @staticmethod
    def generate_otp_code(length: int = 6) -> str:
        return ''.join(random.choices('0123456789', k=length))


class CacheInterface(ABC):
    @abstractmethod
    def get(self, key: str):
        pass

    @abstractmethod
    def set(self, key: str, value: str, timeout: int):
        pass

    @abstractmethod
    def keys(self, pattern: str):
        pass


class DjangoCacheAdapter(CacheInterface):
    def get(self, key: str):
        return cache.get(key)

    def set(self, key: str, value: str, timeout: int):
        cache.set(key, value, timeout)

    def keys(self, pattern: str):
        return cache.keys(pattern)


class SMSSenderInterface(ABC):
    @abstractmethod
    def send(self, phone_number: str, message: str) -> bool:
        pass


class ConsoleSMSSender(SMSSenderInterface):
    def send(self, phone_number: str, otp_code: str) -> bool:
        print(f"Sending SMS to {phone_number}: {otp_code}")
        return True


class SMSValidationStrategy(ABC):
    def __init__(self, phone_number: str, **kwargs):
        self.phone_number = phone_number
        self.kwargs = kwargs

    @abstractmethod
    def validate(self):
        pass

    def _get_user_query(self):
        return {"phone_number": self.phone_number}


class AuthValidation(SMSValidationStrategy):
    def validate(self):
        user = User.objects.filter(**self._get_user_query()).first()
        if user:
            raise ValidationError(_("User exists with this phone number"))


class ForgotPasswordValidation(SMSValidationStrategy):
    def validate(self):
        user = User.objects.filter(**self._get_user_query()).first()
        if not user:
            raise ValidationError(_("User does not exist with this phone number"))


class SMSValidationFactory:
    strategies = {
        SendOTPType.AUTH: AuthValidation,
        SendOTPType.FORGOT_PASSWORD: ForgotPasswordValidation
    }

    @classmethod
    def get_strategy(cls, send_type, phone_number, **kwargs):
        strategy_class = cls.strategies.get(send_type)
        if not strategy_class:
            raise ValueError("Unsupported send type")
        return strategy_class(phone_number, **kwargs)


class SendSMSService:
    SMS_EXPIRE_TIME = 120  # 2 minute

    def __init__(
            self,
            phone_number: str,
            send_type: str,
            **kwargs
    ):
        self.phone_number = phone_number
        self.send_type = send_type
        self.cache = DjangoCacheAdapter()
        self.sms_sender = ConsoleSMSSender()
        self.kwargs = kwargs

        validator = SMSValidationFactory.get_strategy(send_type, phone_number, **kwargs)
        validator.validate()

        self.session = OTPUtils.generate_session()
        self.otp_code = OTPUtils.generate_otp_code()

        otp_sent_key = OTPUtils.generate_cache_key(f"{send_type}_sent", phone_number)
        if cache.get(otp_sent_key):
            raise ValidationError(_("OTP Already sent"))

    def send_sms(self) -> str:
        self.otp_code = "081020"

        self.cache_key = OTPUtils.generate_cache_key(self.send_type, self.phone_number, self.session)
        cache.set(self.cache_key, self.otp_code, timeout=self.SMS_EXPIRE_TIME)

        otp_sent_key = OTPUtils.generate_cache_key(f"{self.send_type}_sent", self.phone_number)
        cache.set(otp_sent_key, True, timeout=self.SMS_EXPIRE_TIME)

        send = self.sms_sender.send(self.phone_number, self.otp_code)
        if not send:
            raise ValidationError(_("Failed to send SMS"))
        return self.session
