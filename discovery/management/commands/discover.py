import time
import traceback
from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from discovery.Discovery import Discovery
from discovery.Logger import Logger


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            print(
                '\nRunning discovery. Logging to logs/%s.log\n'
                % time.strftime('%Y%m%d')
            )
            job = Discovery()
            job.run()
            job._send_email_report()
        except Exception, e:
            Logger.error(traceback.format_exc())
            error = 'TYPE: %s\nARGS: %s\nMESSAGE: %s' % (
                type(e).__name__,
                e.args,
                e.message
            )
            self.send_error_email(error)

    def send_error_email(self, error):
        if settings.EMAIL_HOST_USER != 'YOUR_GMAIL_ADDRESS':
            subject = '[scotuswebcites] Scraper Error Notice'
            message = (
                'Your scotuswebcites discovery scraper encountered an error:'
                '\n\n%s\n\n Please check server logs for more details.' % error
            )
            send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.CONTACT_EMAIL])
