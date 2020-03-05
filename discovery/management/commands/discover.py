import time
import traceback
from django.conf import settings
from django.core.management.base import BaseCommand
from discovery.Discovery import Discovery
from discovery.Logger import Logger
from scotuswebcites.mail import send_email


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            print('\nRunning discovery. Logging to logs/%s.log\n' % time.strftime('%Y%m%d'))
            job = Discovery()
            job.run()
            job.send_email_report()
        except Exception as e:
            Logger.error(traceback.format_exc())
            error = 'FAILED DISCOVER ERROR: %s' % e
            self.send_error_email(error)

    def send_error_email(self, error):
        if settings.EMAIL_HOST_USER != 'YOUR_GMAIL_ADDRESS':
            subject = '[scotuswebcites] Scraper Error Notice'
            body = (
                'Your scotuswebcites discovery scraper encountered an error:'
                '\n\n%s\n\n Please check server logs for more details.' % error
            )
            send_email(subject, body, settings.CONTACT_EMAIL)
