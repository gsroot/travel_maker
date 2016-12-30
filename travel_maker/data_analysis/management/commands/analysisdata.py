from django.core.management import BaseCommand

from travel_maker.data_analysis.management.analyzers import BlogDataAnalizer


class Command(BaseCommand):
    help = 'Analysis data'

    def __init__(self):
        super(Command, self).__init__()
        self.analizers = [
            BlogDataAnalizer()
        ]

    def handle(self, *args, **options):
        for analizer in self.analizers:
            analizer.run()
        return 'analysis data process complete.'