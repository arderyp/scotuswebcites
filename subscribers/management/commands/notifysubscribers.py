from django.utils import timezone
from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.template.loader import get_template
from django.template import Context
from django.core.mail import EmailMultiAlternatives
from subscribers.models import Subscriber
from citations.models import Citation
from discovery.Logger import Logger

class Command(NoArgsCommand):
    help = 'Notify subscribers about newly validated citations'

    def handle_noargs(self, **options):
        Logger.info("RUNNING NOTIFY SUBSCRIBERS FUNCTION: %s" % timezone.now())
        newly_verified_citations = Citation.objects.filter(
            validated__isnull=False,
            notified_subscribers__isnull=True,
        )
        if newly_verified_citations:
            Logger.info('Found %d newly verified citations' % len(newly_verified_citations))

            # Send email notifications to subscribers
            subscribers = Subscriber.objects.filter(subscribed=True)
            if subscribers:
                Logger.info('Emailing newly verified citations to %d subscribers' % len(subscribers))
                for subscriber in subscribers:
                    self._send_email(subscriber, newly_verified_citations)

            # Update citations records to indicate that notifications sent
            for citation in newly_verified_citations:
                citation.notified_subscribers = timezone.now()
                citation.save()

    def _send_email(self, subscriber, citations):
        if settings.EMAIL_HOST_USER != 'YOUR_GMAIL_ADDRESS':
            Logger.info('+sending subscriber notification to %s' % subscriber.email)
            html = get_template('newly_verified_citations_email.html')
            context = Context({
                'subscriber': subscriber,
                'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else False,
                'citations': citations,
                'contact_email': settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else False
            })
            body = html.render(context)
            subject = '[scotuswebcites] New citations discovered and verified'
            sender = settings.EMAIL_HOST_USER
            recipient = subscriber.email
            msg = EmailMultiAlternatives(subject, body, sender, [recipient])
            msg.attach_alternative(body, "text/html")
            msg.send()
