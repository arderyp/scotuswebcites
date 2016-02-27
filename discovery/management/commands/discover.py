from django.core.management.base import NoArgsCommand
from discovery.Discovery import Discovery

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        d = Discovery()
        d.run()
