import time
import traceback

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import NoArgsCommand
from discovery.Discovery import Discovery
from discovery.Logger import Logger

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        try:
            print('\nRunning discovery. Logging to logs/%s.log\n' % time.strftime('%Y%m%d'))
            job = Discovery()
            job.run()
            job.send_email_report()
        except:
            Logger.error(traceback.format_exc())
            self.send_error_email()

    def send_error_email(self):
        if settings.EMAIL_HOST_USER != 'YOUR_GMAIL_ADDRESS':
            subject = '[scotuswebcites] Scraper Error Notice'
            message = 'Your scotuswebcites discovery scraper encountered an error.  Please check server logs for details.'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [settings.CONTACT_EMAIL])
