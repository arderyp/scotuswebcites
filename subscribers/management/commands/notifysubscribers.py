from django.utils import timezone
from django.conf import settings
from django.core.management.base import BaseCommand
from django.template.loader import get_template
from citations.models import Citation
from discovery.Logger import Logger
from scotuswebcites.mail import send_email
from subscribers.models import Subscriber


class Command(BaseCommand):
    help = 'Notify subscribers about newly validated citations'

    def handle(self, *args, **options):
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
            template = get_template('newly_verified_citations_email.html')
            template_parameters = {
                'subscriber': subscriber,
                'domain': settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else False,
                'citations': citations,
                'contact_email': settings.SENDER_EMAIL if settings.SENDER_EMAIL else False
            }
            body = template.render(template_parameters)
            subject = '[scotuswebcites] New citations discovered and verified'
            send_email(subject, body, subscriber.email)
