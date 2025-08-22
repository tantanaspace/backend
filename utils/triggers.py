from django.conf import settings

from telegram import Bot, ParseMode
from sentry_sdk.types import Event, Hint


def sentry_before_send_trigger(event: Event, hint: Hint):
    result_text = ""
    
    if settings.DEBUG:
        result_text += "🔴 <b>DEBUG mode is ON</b> ⚠️\n\n"

    for exception_values in event.get("exception", {}).get("values", []):
        result_text += f"{exception_values.get('type')} - {exception_values.get('value')}\n\n"

        for frame in exception_values.get("stacktrace", {}).get("frames", []):
            if frame.get('in_app') is True:
                result_text += f"<code> {frame.get('filename')}:{frame.get('lineno')} </code>\n"
                result_text += "<pre lang='python'>\n"
                for line in frame.get("pre_context", []): result_text += line + "\n"  # noqa
                result_text += f"🔥{frame.get('context_line')}🔥\n"
                for line in frame.get("post_context", []): result_text += line + "\n"  # noqa
                result_text += "</pre>\n"
    if result_text:
        Bot(token=settings.SENTRY_BOT_TOKEN).send_message(
            chat_id=settings.SENTRY_CHAT_ID, 
            message_thread_id=settings.SENTRY_THREAD_ID, 
            text=result_text, 
            parse_mode=ParseMode.HTML
        )

    return event
