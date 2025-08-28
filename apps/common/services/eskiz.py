import sys
import json
import hashlib
import logging
import requests
from uuid import uuid4

from django.core.cache import cache
from django.utils import timezone
from django.conf import settings

from phonenumber_field.phonenumber import PhoneNumber

from apps.common.models import OTPLog


class EskizInterface:
    def __init__(self):
        self.base_url = f"https://notify.eskiz.uz"
        self.username = settings.ESKIZ_CREDENTIALS['username']
        self.password = settings.ESKIZ_CREDENTIALS['secret_key']
        self.callback_url = settings.ESKIZ_CREDENTIALS['callback_url']
        self.from_number = settings.ESKIZ_CREDENTIALS['from_number']
        self.cache_key = 'eskiz_access_token'

    @property
    def access_token(self):
        eskiz_access_token_data = cache.get(self.cache_key)

        if eskiz_access_token_data:
            try:
                eskiz_access_token_data = json.loads(eskiz_access_token_data)
                expire_time = timezone.datetime.fromisoformat(eskiz_access_token_data.get('expire_time', ''))
            except (json.JSONDecodeError, ValueError):
                logging.error("Error while parsing Eskiz access token data from cache")
                eskiz_access_token_data = None

        if not eskiz_access_token_data or expire_time < timezone.now():
            try:
                response = requests.post(
                    f"{self.base_url}/api/auth/login",
                    data={"email": self.username, "password": self.password},
                )
                response.raise_for_status()
                response_data = response.json()
            except requests.exceptions.RequestException as e:
                logging.error(f"Eskiz API error: {e}")
                return None
            except ValueError:
                logging.error("Eskiz API response is not JSON")
                return None

            access_token = response_data.get('data', {}).get("token")
            if not access_token:
                logging.error("Eskiz API response does not contain access token")
                return None

            expire_time = (timezone.now() + timezone.timedelta(days=30)).isoformat()
            cache.set(self.cache_key, json.dumps({'access_token': access_token, 'expire_time': expire_time}),
                      timeout=30 * 24 * 60 * 60)

            return access_token

        return eskiz_access_token_data.get('access_token')

    def send_sms(self, phone_number, message):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        data = {
            'mobile_phone': phone_number,
            'message': message,
            'from': self.from_number,
            'callback_url': self.callback_url
        }
        response = requests.post(
            f"{self.base_url}/api/message/sms/send",
            headers=headers,
            json=data
        )
        return response

    @staticmethod
    def confirmation_sms_message(code: str):
        return f"Tantana ilovasiga kirish uchun tasdiqlash kod: {code}"
    
    @staticmethod
    def forgot_password_sms_message(code: str):
        return f"Tantana ilovasining parolini tiklash uchun kod: {code}"


eskiz_interface = EskizInterface()


def send_sms(phone_number: PhoneNumber, message: str):
    """
    Send activation code via SMS
    """
    if "test" not in sys.argv:
        message_id = 'anb%s' % hashlib.md5(str(uuid4()).encode()).hexdigest()[:17]
        response_log = {}
        is_sent = False

        try:
            response = eskiz_interface.send_sms(str(phone_number), message)

            try:
                response_json = response.json()
                is_sent = response.status_code == 200
                message_id = response_json.get('id', message_id)
                
                response_log = {
                    'status_code': response.status_code,
                    'response': response_json
                }
                
            except ValueError:
                response_log = {
                    'status_code': response.status_code,
                    'response': response.text
                }
                is_sent = False

        except requests.exceptions.HTTPError as e:
            is_sent = False
            try:
                error_response = e.response.json() if e.response else {}
            except (ValueError, AttributeError):
                error_response = e.response.text if e.response else str(e)
            
            response_log = {
                'error': str(e),
                'exception_type': type(e).__name__,
                'status_code': getattr(e.response, 'status_code', None) if e.response else None,
                'response': error_response
            }
            
        except Exception as e:
            is_sent = False
            response_log = {
                'error': str(e),
                'exception_type': type(e).__name__
            }
            
            if 'response' in locals():
                try:
                    response_text = response.text
                except:
                    response_text = None
                
                response_log.update({
                    'status_code': getattr(response, 'status_code', None),
                    'response': response_text
                })

        OTPLog.objects.create(
            message_id=message_id,
            phone_number=phone_number,
            text=message,
            is_sent=is_sent,
            sent_at=timezone.now(),
            response_log=response_log
        )
        
        return is_sent