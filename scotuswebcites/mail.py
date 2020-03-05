from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_email(subject: str, body: str, recipient: str):
    if 'YOUR_GMAIL_ADDRESS' in [settings.SENDER_EMAIL, settings.EMAIL_HOST_USER]:
        raise Exception("Email setting not configured")
    sender = settings.SENDER_EMAIL
    bcc = [settings.SENDER_EMAIL]
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=sender,
        to=[recipient],
        bcc=bcc
    )
    email.attach_alternative(body, "text/html")
    email.send()
