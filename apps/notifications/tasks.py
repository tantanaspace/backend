import logging
from typing import List, Optional

from apps.notifications.utils import NotificationSender
from core.celery import app

logger = logging.getLogger(__name__)


@app.task(bind=True)
def send_notification(
    self,
    notification_id: int,
    is_for_everyone: bool = False,
    users_id: Optional[List[int]] = None,
    only_push: bool = False,
):
    sender = NotificationSender(notification_id, is_for_everyone, users_id, only_push)
    result = sender.send()

    if result.get("status") == "error":
        try:
            self.retry(exc=Exception(result["message"]), countdown=30, max_retries=3)
        except Exception as retry_exc:
            logger.error(f"Failed to retry task: {str(retry_exc)}")

    return result
