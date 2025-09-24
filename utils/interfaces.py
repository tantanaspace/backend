import json
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional

from django_redis import get_redis_connection


class RedisKeys:
    """
    Redis keys used for WebSocket messaging service.
    Organized by user and worker related keys.
    """

    DRIVER_WORKER_MAP = "ws:driver_worker_map"
    ADMIN_WORKER_MAP = "ws:admin_worker_map"
    WORKER_STREAM_CHANNEL = "ws:stream:{worker_id}"


class MessageTypes(Enum):
    """
    Enum defining WebSocket message types.
    """

    HOS_REMAINING = "hos_remaining"
    HOS_TIMER = "hos_timer"
    HOS_VIOLATION = "hos_violation"
    HOS_VIOLATION_SIGNAL = "hos_violation_signal"
    MESSAGE = "message"
    SIGNAL = "signal"
    CHAT = "chat"


class BaseWebSocketInterface(ABC):
    """
    Base Interface to send WebSocket messages to users.

    Automatically detects which worker handles a users's connection and
    sends messages to the corresponding Redis stream.

    Uses Redis Streams to enqueue messages for delivery to WebSocket clients.
    """

    def __init__(self, redis_client=None):
        """
        Initialize with a Redis client or default Django Redis connection.

        Args:
            redis_client: Optional custom Redis connection instance.
        """
        self.redis = redis_client or get_redis_connection("default")

    @property
    @abstractmethod
    def user_worker_map_key(self) -> str:
        """Return Redis hash key used to store user_id → worker_id mapping."""

    def _get_user_stream(self, user_id: int) -> Optional[str]:
        """
        Get the Redis stream key for the user's given message type.

        Checks if the user is currently connected by verifying the worker assignment.

        Args:
            user_id: User's unique identifier.
            message_type: Type of message to send.

        Returns:
            The Redis stream key string or None if the user is not connected.
        """
        worker_id = self.redis.hget(self.user_worker_map_key, str(user_id))
        if not worker_id:
            return None

        return RedisKeys.WORKER_STREAM_CHANNEL.format(worker_id=worker_id.decode())

    def _send_message(
        self, user_id: int, message_type: MessageTypes, data: Dict[str, Any]
    ) -> bool:
        """
        Generic method to send a message of a given type to a user.

        Args:
            user_id: User's unique identifier.
            message_type: Type of the message.
            data: Message payload data.

        Returns:
            True if message was queued successfully, False if user not connected.
        """
        stream_key = self._get_user_stream(user_id)
        if not stream_key:
            return False

        message = {
            "user_id": user_id,
            "type": message_type.value,
            "timestamp": time.time(),
            "data": json.dumps(data),
        }

        # Redis xadd expects field-value pairs; convert all values to strings
        self.redis.xadd(stream_key, message)
        return True

    def send_hos_remaining(self, user_id: int, remaining_data: Dict[str, Any]) -> bool:
        """
        Send Hours of Service (HOS) remaining data to a user.

        Args:
            user_id: User's unique identifier.
            remaining_data: Remaining information payload.

        Returns:
            True if message sent, False if user offline.
        """
        return self._send_message(user_id, MessageTypes.HOS_REMAINING, remaining_data)

    def send_hos_timer(self, user_id: int, timer_data: Dict[str, Any]) -> bool:
        """
        Send Hours of Service (HOS) timer update to a user.

        Args:
            user_id: User's unique identifier.
            timer_data: Timer information payload.

        Returns:
            True if message sent, False if user offline.
        """
        return self._send_message(user_id, MessageTypes.HOS_TIMER, timer_data)

    def send_hos_violation(self, user_id: int, violation_data: Dict[str, Any]) -> bool:
        """
        Send HOS violation alert to a user.

        Args:
            user_id: User's unique identifier.
            violation_data: Violation details payload.

        Returns:
            True if message sent, False if user offline.
        """
        return self._send_message(user_id, MessageTypes.HOS_VIOLATION, violation_data)

    def send_hos_violation_signal(
        self, user_id: int, violation_signal_data: Dict[str, Any]
    ) -> bool:
        """
        Send HOS violation signal alert to a user.

        Args:
            user_id: User's unique identifier.
            violation_signal_data: Violation signal details payload.

        Returns:
            True if message sent, False if user offline.
        """
        return self._send_message(
            user_id, MessageTypes.HOS_VIOLATION_SIGNAL, violation_signal_data
        )

    def send_signal(self, user_id: int, signal_data: Dict[str, Any]) -> bool:
        """
        Send a signal message to a user.

        Args:
            user_id: User's unique identifier.
            signal_data: Signal data payload.

        Returns:
            True if message sent, False if user offline.
        """
        return self._send_message(user_id, MessageTypes.SIGNAL, signal_data)

    def send_message(self, user_id: int, message_data: Dict[str, Any]) -> bool:
        """
        Send a generic message to a user.

        Args:
            user_id: User's unique identifier.
            message_data: Message payload.

        Returns:
            True if message sent, False if user offline.
        """
        return self._send_message(user_id, MessageTypes.MESSAGE, message_data)

    def send_chat_message(self, user_id: int, chat_data: Dict[str, Any]) -> bool:
        """
        Send a chat message to a user.

        Args:
            user_id: User's unique identifier.
            chat_data: Chat message payload.

        Returns:
            True if message sent, False if user offline.
        """
        return self._send_message(user_id, MessageTypes.CHAT, chat_data)

    def is_user_online(self, user_id: int) -> bool:
        """
        Check if a user is currently connected to any WebSocket worker.

        Args:
            user_id: User's unique identifier.

        Returns:
            True if the user is online, False otherwise.
        """
        return bool(self.redis.hget(self.user_worker_map_key, str(user_id)))

    def online_users_count(self) -> int:
        """
        Get the number of online users.
        """
        return self.redis.hlen(self.user_worker_map_key)


class DriverWebSocketInterface(BaseWebSocketInterface):
    @property
    def user_worker_map_key(self) -> str:
        return RedisKeys.DRIVER_WORKER_MAP


class AdminWebSocketInterface(BaseWebSocketInterface):
    @property
    def user_worker_map_key(self) -> str:
        return RedisKeys.ADMIN_WORKER_MAP
