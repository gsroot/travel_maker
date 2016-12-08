from django.core.management.base import BaseCommand

from travel_maker.google_data_collector.management.collectors import GooglePlaceInfoCollector, \
    GooglePlaceReviewInfoCollector


class Command(BaseCommand):
    help = 'Collect google data'

    def __init__(self):
        super(Command, self).__init__()
        self.collectors = [
            GooglePlaceInfoCollector(),
            GooglePlaceReviewInfoCollector(),
        ]

    def handle(self, *args, **options):
        for collector in self.collectors:
            collector.run()
        return 'collecting data process complete.'
