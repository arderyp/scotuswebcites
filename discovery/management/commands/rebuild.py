import os
import glob
from django.core.management.base import BaseCommand
from django.core.management import call_command
from scotuswebcites import settings


class Command(BaseCommand):
    def handle(self, *args, **options):
        call_command('migrate', 'opinions', 'zero')
        call_command('migrate', 'citations', 'zero')
        call_command('migrate')
        pdf_files = glob.glob(settings.PDF_DIR + '*.pdf')
        for pdf in pdf_files:
            os.remove(pdf)
