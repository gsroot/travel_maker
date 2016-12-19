from django.core.management.base import BaseCommand

from travel_maker.blog_data_collector.management.collectors import BlogDataCollector


class Command(BaseCommand):
    help = 'Collect blog data'

    def __init__(self):
        super(Command, self).__init__()
        self.collectors = [
            BlogDataCollector()
        ]

    def handle(self, *args, **options):
        for collector in self.collectors:
            collector.run()
        return 'collecting data process complete.'
