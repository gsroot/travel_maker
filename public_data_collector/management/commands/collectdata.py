from django.core.management.base import BaseCommand

from public_data_collector.management.collectors import PublicDataCollector


class Command(PublicDataCollector, BaseCommand):
    help = 'Collect public data'

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        self.run()
        return 'collecting data process complete.'
