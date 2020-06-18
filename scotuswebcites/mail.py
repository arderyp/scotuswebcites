from django.conf import settings
from django.core.mail import EmailMultiAlternatives


def send_email(subject: str, body: str, recipient: str):
    if 'YOUR_GMAIL_ADDRESS' in [settings.SENDER_EMAIL, settings.EMAIL_HOST_USER]:
        raise Exception("Email setting not configured")
    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=settings.SENDER_EMAIL,
        to=[recipient],
        bcc=[settings.SENDER_EMAIL]
    )
    email.attach_alternative(body, "text/html")
    email.send()
