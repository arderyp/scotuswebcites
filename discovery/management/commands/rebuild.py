from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from scotus import settings
import os
import glob

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        call_command('migrate', 'opinions', 'zero')
        call_command('migrate', 'citations', 'zero')
        call_command('migrate')
        pdf_files = glob.glob(settings.PDF_DIR + '*.pdf')
        for pdf in pdf_files:
            os.remove(pdf)
