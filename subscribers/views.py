from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.conf import settings
from django.template.loader import get_template
from subscribers.models import Subscriber


def sign_up(request):
    if request.method == 'POST':
        if settings.EMAIL_HOST_USER == 'YOUR_GMAIL_ADDRESS':
            flash_type = messages.WARNING
            flash_message = 'It looks like the host is not configured to send emails quite yet'
        else:
            proceed = True
            valid_email = True
            email = request.POST.get('email', '')
            if Subscriber.objects.filter(email=email):
                subscriber = Subscriber.objects.get(email=email)
                if subscriber.subscribed:
                    proceed = False
                    flash_type = messages.SUCCESS
                    flash_message = 'Good news, it looks like you are already subscribed!'
            else:
                try:
                    subscriber = Subscriber(email=email)
                    subscriber._set_hash()
                    subscriber.save()
                except:
                    valid_email = False
            if valid_email and proceed:
                try:
                    _send_confirmation_email(request, subscriber)
                    flash_type = messages.SUCCESS
                    flash_message = "Thanks for subscribing! We've sent a confirmation email to %s." % email
                except:
                    valid_email = False
            if not valid_email:
                flash_type = messages.WARNING
                flash_message = 'It looks like you submitted an invalid email address'
        messages.add_message(request, flash_type, flash_message)

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def subscribe(request, hash_key):
    subsciber = Subscriber.objects.get(hash_key=hash_key)
    if subsciber and not subsciber.subscribed:
        subsciber.subscribed = True
        subsciber.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Thanks for confirming your subscription!'
        )
    return HttpResponseRedirect('/')

def unsubscribe(request, hash_key):
    subsciber = Subscriber.objects.get(hash_key=hash_key)
    if subsciber and subsciber.subscribed:
        subsciber.subscribed = False
        subsciber.save()
        messages.add_message(
            request,
            messages.SUCCESS,
            'You have successfully unsubscribed. Thanks for using our service!'
        )
    return HttpResponseRedirect('/')

def _send_confirmation_email(request, subscriber):
    url_base = request.build_absolute_uri('/')
    html = get_template('confirm_subscription_email.html')
    context = Context({
        'subscriber': subscriber,
        'url_base': url_base.rstrip('/'),
        'contact_email': settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else False
    })
    body = html.render(context)
    subject = '[scotuswebcites] Subscriber confirmation'
    sender = settings.EMAIL_HOST_USER
    recipient = subscriber.email
    msg = EmailMultiAlternatives(subject, body, sender, [recipient])
    msg.attach_alternative(body, "text/html")
    msg.send()

