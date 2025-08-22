import logging
from typing import Dict, List, Optional, Union, Any
from firebase_admin import messaging, initialize_app, credentials
from collections import defaultdict

from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.notifications.models import Notification, UserNotification, CustomFCMDevice

logger = logging.getLogger(__name__)


class FirebaseMessaging:
    def __init__(self, raise_exception: bool = False):
        if not getattr(settings, 'FIREBASE_CREDENTIAL_PATH', None):
            raise Exception(
                "Firebase credential file path are not provided in settings. "
                "Example: FIREBASE_CREDENTIAL_PATH = 'path/to/your/credential.json'"
            )

        if not getattr(settings, 'FIREBASE_APP', None):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIAL_PATH)
            settings.FIREBASE_APP = initialize_app(cred)

        self.firebase = settings.FIREBASE_APP
        self.raise_exception = raise_exception

    @staticmethod
    def __create_apns_config(title: str, body: str, image: str | None = None, badge: int = 0):
        """
        Creates APNS configuration for a notification.

        :param title: Notification title
        :param body: Notification body
        :param image: The URL of the image to be displayed in the notification (optional).
        :param badge: The number to display in a badge on your app's icon.
        :return: An APNSConfig object.
        """
        aps_alert = messaging.ApsAlert(
            title=title,
            body=body,
            launch_image=None,
            custom_data=None
        )

        aps = messaging.Aps(
            alert=aps_alert,
            sound=messaging.CriticalSound('default', critical=True, volume=1.0),
            badge=badge,
            thread_id=None,
            mutable_content=True,
            custom_data=None
        )

        apns_payload = messaging.APNSPayload(
            aps=aps,
            custom_data=None
        )

        apns_fcm_options = messaging.APNSFCMOptions(
            analytics_label=None,
            image=image
        )

        apns_config = messaging.APNSConfig(
            headers=None,
            payload=apns_payload,
            fcm_options=apns_fcm_options
        )

        return apns_config

    @staticmethod
    def __create_android_config(title: str, body: str, image: str | None = None, badge: int = 0):
        android_notification = messaging.AndroidNotification(
            title=title,
            body=body,
            image=image,
            color='#ffffff',
            sound=None,
            priority='max',
            visibility='public',
            light_settings=messaging.LightSettings(
                color='#f45342',
                light_on_duration_millis=100,
                light_off_duration_millis=100
            ),
            vibrate_timings_millis=[100, 200, 300, 400],
            notification_count=badge
        )

        android_fcm_options = messaging.AndroidFCMOptions(
            analytics_label=None,
        )

        android_config = messaging.AndroidConfig(
            priority='high',
            restricted_package_name=None,
            data=None,
            notification=android_notification,
            fcm_options=android_fcm_options
        )

        return android_config

    @staticmethod
    def __create_fcm_config(title: str, body: str, image: str | None = None):
        return messaging.Notification(
            title=title,
            body=body,
            image=image,
        )

    @staticmethod
    def _chunk_tokens(tokens: List[str], chunk_size: int = 500) -> List[List[str]]:
        """
        Split tokens into chunks to avoid exceeding Firebase limits.
        """
        return [tokens[i:i + chunk_size] for i in range(0, len(tokens), chunk_size)]

    def _send_message(self, message: messaging.Message) -> Dict[str, Union[str, bool]]:
        """
        Sends a single message.
        :param message: The `messaging.Message` object
        :return: Dict containing success status and message ID or error
        """
        try:
            message_id = messaging.send(message, app=self.firebase)
            return {
                'success': True,
                'message_id': message_id,
                'token': message.token
            }
        except messaging.exceptions.FirebaseError as e:
            error_msg = f"Firebase error while sending message: {str(e)}"
            logger.error(error_msg)
            if self.raise_exception:
                raise Exception(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'token': message.token
            }
        except Exception as e:
            error_msg = f"Unexpected error while sending message: {str(e)}"
            logger.error(error_msg)
            if self.raise_exception:
                raise Exception(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'token': message.token
            }

    def _send_each(self, messages: List[messaging.Message]) -> Dict[str, Union[List[Dict], str]]:
        """
        Sends a message to each token.
        :param messages: List of `messaging.Message` objects
        :return: Dict containing results for each message
        """
        try:
            response = messaging.send_each(messages, app=self.firebase)
            results = []
            
            for idx, result in enumerate(response.responses):
                message = messages[idx]
                if result.success:
                    results.append({
                        'success': True,
                        'message_id': result.message_id,
                        'token': message.token
                    })
                else:
                    results.append({
                        'success': False,
                        'error': result.exception,
                        'token': message.token
                    })
            
            return {'success': True, 'results': results}
        except Exception as e:
            error_msg = f"Error while sending messages: {str(e)}"
            logger.error(error_msg)
            if self.raise_exception:
                raise Exception(error_msg)
            return {'success': False, 'error': error_msg}

    def _send_each_for_multicast(self, multicast_message: messaging.MulticastMessage) -> Dict[str, Union[List[Dict], str]]:
        """
        Sends a message to each token in the `messaging.MulticastMessage` object.
        :param multicast_message: The `messaging.MulticastMessage` object
        :return: Dict containing results for each token
        """
        try:
            response = messaging.send_each_for_multicast(multicast_message, app=self.firebase)
            results = []
            
            for idx, result in enumerate(response.responses):
                token = multicast_message.tokens[idx]
                if result.success:
                    results.append({
                        'success': True,
                        'message_id': result.message_id,
                        'token': token
                    })
                else:
                    results.append({
                        'success': False,
                        'error': result.exception,
                        'token': token
                    })
            
            return {'success': True, 'results': results}
        except Exception as e:
            error_msg = f"Error while sending multicast message: {str(e)}"
            logger.error(error_msg)
            if self.raise_exception:
                raise Exception(error_msg)
            return {'success': False, 'error': error_msg}

    def subscribe_to_topic(self, tokens, topic):
        """
        Subscribes devices to a specific topic.
        :param tokens: List of device tokens
        :param topic: Topic name
        """

        try:
            return messaging.subscribe_to_topic(tokens, topic)
        except (messaging.exceptions.FirebaseError, ValueError):
            if self.raise_exception:
                raise Exception("Failed to subscribe to the topic.")

    def unsubscribe_from_topic(self, tokens, topic):
        """
        Unsubscribes devices from a topic.
        :param tokens: List of device tokens
        :param topic: Topic name
        """
        try:
            return messaging.unsubscribe_from_topic(tokens, topic)
        except (messaging.exceptions.FirebaseError, ValueError):
            if self.raise_exception:
                raise Exception("Failed to unsubscribe from the topic.")

    def create_message(
            self,
            title: str,
            body: str,
            token: str,
            image: str | None = None,
            badge: int = 0,
            topic: str | None = None,
            data: dict | None = None,
    ) -> messaging.Message:
        """
        Create a message.
        :param title: Notification title
        :param body: Notification body
        :param token: Device token
        :param image: The URL of the image to be displayed in the notification.
        :param badge: The number to display in a badge on your app's icon.
        :param topic: The topic to which the message should be sent.
        :param data: Data to be sent in the message
        :return: A messaging.Message instance.
        """
        if not (title and body and token):
            raise Exception("Title, body, and token are required to create a message.")

        message = messaging.Message(
            notification=self.__create_fcm_config(title, body, image),
            apns=self.__create_apns_config(title, body, image, badge),
            android=self.__create_android_config(title, body, image, badge),
            data=data,
            token=token,
            topic=topic,
        )

        return message

    def create_multicast_messages(
            self,
            title: str,
            body: str,
            image: str | None = None,
            badge: int = 0,
            data: dict | None = None,
            tokens: list | None = None,
    ) -> List[messaging.MulticastMessage]:
        """
        Create multicast messages.
        :param title: Notification title
        :param body: Notification body
        :param image: The URL of the image to be displayed in the notification.
        :param badge: The number to display in a badge on your app's icon.
        :param data: Data to be sent in the message
        :param tokens: List of device tokens
        :return: A list of messaging.MulticastMessage instances.
        """
        if not (title and body and tokens):
            raise Exception("Title, body, and tokens are required to create multicast messages.")

        if not isinstance(tokens, list):
            raise Exception("Tokens should be a list of device tokens.")

        messages = []
        for chunk in self._chunk_tokens(tokens):
            messages.append(messaging.MulticastMessage(
                notification=self.__create_fcm_config(title, body, image),
                apns=self.__create_apns_config(title, body, image, badge),
                android=self.__create_android_config(title, body, image, badge),
                data=data,
                tokens=chunk,
            ))

        return messages

    def send(
            self,
            message: Optional[messaging.Message] = None,
            messages: Optional[List[messaging.Message]] = None,
            multicast_messages: Optional[List[messaging.MulticastMessage]] = None
    ) -> Dict[str, Union[List[Dict], str]]:
        """
        Sends a message to the FCM server.
        :param message: A `messaging.Message` object
        :param messages: List of `messaging.Message` objects
        :param multicast_messages: List of `messaging.MulticastMessage` objects
        :return: Dict containing results of the send operation
        """
        if message:
            return self._send_message(message)
        elif messages:
            return self._send_each(messages)
        elif multicast_messages:
            results = []
            for multicast_message in multicast_messages:
                result = self._send_each_for_multicast(multicast_message)
                if result['success']:
                    results.extend(result['results'])
                else:
                    logger.error(f"Failed to send multicast message: {result['error']}")
            return {'success': True, 'results': results}
        else:
            raise Exception("No message provided to send.")


class NotificationSender:
    def __init__(self, notification_id: int, is_for_everyone: bool = False, users_id: Optional[List[int]] = None, only_push: bool = False):
        self.notification_id = notification_id
        self.is_for_everyone = is_for_everyone
        self.users_id = users_id
        self.only_push = only_push
        self.notification = None
        self.token_status = {'success': set(), 'failed': set()}
        self._firebase_messaging = FirebaseMessaging(raise_exception=False)

    def _get_notification(self) -> Notification:
        try:
            return Notification.objects.get(id=self.notification_id)
        except Notification.DoesNotExist:
            raise ValueError('Notification does not exist.')

    def _validate_notification_status(self) -> None:
        if self.notification.status == Notification.Status.IN_PROCESS:
            raise ValueError('This notification sending task is in progress. Already running.')

    def _get_active_users(self) -> List[int]:
        if self.is_for_everyone:
            return list(get_user_model().objects.filter(is_active=True).values_list('id', flat=True))
        return self.users_id or []

    def _create_user_notifications(self, users_id: List[int]) -> List[UserNotification]:
        if self.only_push:
            return []

        with transaction.atomic():
            return UserNotification.objects.bulk_create([
                UserNotification(
                    user_id=user_id,
                    notification_id=self.notification_id,
                    data=self.notification.get_notification_data(),
                    is_sent=False,
                )
                for user_id in users_id
            ])

    def _get_tokens_by_language(self, users_id: List[int]) -> Dict[str, List[str]]:
        tokens = CustomFCMDevice.objects.filter(
            user__in=users_id,
            active=True,
        ).values('registration_id', 'user__language', 'user_id')

        tokens_by_language = defaultdict(list)
        for token in tokens:
            language = token['user__language']
            if language in dict(settings.LANGUAGES):
                tokens_by_language[language].append(token['registration_id'])

        return tokens_by_language

    def _send_multicast_message(self, lang: str, tokens: List[str]) -> None:
        title = getattr(self.notification, f'title_{lang}', self.notification.title)
        body = getattr(self.notification, f'body_text_{lang}', self.notification.body_text)

        try:
            messages = self._firebase_messaging.create_multicast_messages(
                title=title,
                body=body,
                tokens=tokens,
                data=self.notification.get_notification_data()
            )
            response = self._firebase_messaging.send(multicast_messages=messages)

            if isinstance(response, dict) and response.get('success'):
                self._process_multicast_results(response.get('results', []), tokens)
            else:
                self._handle_send_failure(lang, tokens, response)
        except Exception as e:
            self._handle_send_failure(lang, tokens, str(e))

    def _send_single_message(self, lang: str, token: str) -> None:
        title = getattr(self.notification, f'title_{lang}', self.notification.title)
        body = getattr(self.notification, f'body_text_{lang}', self.notification.body_text)

        try:
            message = self._firebase_messaging.create_message(
                title=title,
                body=body,
                token=token,
                data=self.notification.get_notification_data()
            )
            response = self._firebase_messaging.send(message)

            if isinstance(response, dict) and response.get('success'):
                self.token_status['success'].add(token)
            else:
                self._handle_send_failure(lang, [token], response)
        except Exception as e:
            self._handle_send_failure(lang, [token], str(e))

    def _process_multicast_results(self, results: List[Dict], tokens: List[str]) -> None:
        for idx, token_result in enumerate(results):
            token = tokens[idx]
            if token_result.get('success'):
                self.token_status['success'].add(token)
            else:
                self.token_status['failed'].add(token)
                logger.error(f"Failed to send to token {token}: {token_result.get('error')}")

    def _handle_send_failure(self, lang: str, tokens: List[str], error: Any) -> None:
        error_msg = str(error.get('error', 'Unknown error')) if isinstance(error, dict) else str(error)
        logger.error(f"Failed to send message to {lang}: {error_msg}")
        for token in tokens:
            self.token_status['failed'].add(token)

    def _update_notification_status(self) -> None:
        if not self.only_push:
            now = timezone.now()
            with transaction.atomic():
                successful_user_ids = CustomFCMDevice.objects.filter(
                    registration_id__in=self.token_status['success']
                ).values_list('user_id', flat=True)

                UserNotification.objects.filter(
                    notification=self.notification,
                    user_id__in=successful_user_ids
                ).update(
                    is_sent=True,
                    sent_at=now
                )

    def _get_result_stats(self, user_notifications: List[UserNotification], total_tokens: int) -> Dict:
        return {
            'total_users': len(user_notifications) if not self.only_push else 0,
            'total_tokens': total_tokens,
            'sent_tokens': len(self.token_status['success']),
            'failed_tokens': len(self.token_status['failed'])
        }

    def send(self) -> Dict:
        try:
            self.notification = self._get_notification()
            self._validate_notification_status()

            self.notification.status = Notification.Status.IN_PROCESS
            self.notification.save(update_fields=["status"])

            users_id = self._get_active_users()
            user_notifications = self._create_user_notifications(users_id)
            tokens_by_language = self._get_tokens_by_language(users_id)

            for lang, tokens in tokens_by_language.items():
                if not tokens:
                    continue

                if len(tokens) > 1:
                    self._send_multicast_message(lang, tokens)
                else:
                    self._send_single_message(lang, tokens[0])

            self._update_notification_status()

            result = self._get_result_stats(user_notifications, sum(len(tokens) for tokens in tokens_by_language.values()))
            
            self.notification.status = Notification.Status.COMPLETED
            self.notification.save(update_fields=["status"])

            return result

        except Exception as exc:
            error_msg = str(exc)
            logger.error(f"Unexpected error in send_notification task: {error_msg}")
            if self.notification:
                self.notification.status = Notification.Status.FAILED
                self.notification.save(update_fields=["status"])
            
            return {
                'status': 'error',
                'message': error_msg
            }
