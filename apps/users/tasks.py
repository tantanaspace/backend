from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from core.celery import app


@app.task
def send_html_email(
    subject: str,
    to_email: str,
    template_name: str,
    context: dict,
    from_email: str = None,
):
    """
    Universal sending of HTML-letter via Celery.
    :param subject: Subject of the letter
    :param to_email: To whom to send
    :param template_name: Template name (for example, 'emails/reset_password.html')
    :param context: Dictionary with variables for the template
    :param from_email: From whom (if not passed, taken from the settings)
    """
    from django.conf import settings

    if not from_email:
        from_email = settings.DEFAULT_FROM_EMAIL

    html_content = render_to_string(template_name, context)
    text_content = context.get("text_message") or "You have a new notification."

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
