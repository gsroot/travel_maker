from django.core.management.base import BaseCommand

from config.settings.base import TRAVEL_API_SECRET_KEYS
from travel_maker.public_data_collector.management.collectors import WebCollector, \
    ContentTypeCollector, AreacodeWebCollector, CategorycodeWebCollector, TravelInfoWebCollector, \
    TravelOverviewInfoWebCollector, TravelIntroInfoWebCollector, TravelDetailInfoWebCollector, \
    TravelImageInfoWebCollector


class Command(BaseCommand):
    help = 'Collect public data'

    def __init__(self):
        super(Command, self).__init__()

        WebCollector.service_keys = TRAVEL_API_SECRET_KEYS
        WebCollector.service_key = WebCollector.service_keys[0]

        self.collectors = [
            ContentTypeCollector(),
            AreacodeWebCollector(),
            CategorycodeWebCollector(),
            TravelInfoWebCollector(),
            TravelOverviewInfoWebCollector(),
            TravelIntroInfoWebCollector(),
            TravelDetailInfoWebCollector(),
            TravelImageInfoWebCollector(),
        ]

    def handle(self, *args, **options):
        for idx, key in enumerate(WebCollector.service_keys):
            for collector in self.self.collectors:
                collector.run()
            WebCollector.change_service_key(idx + 1)

        return 'collecting data process complete.'
