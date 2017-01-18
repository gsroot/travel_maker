from django.core.management import BaseCommand

from travel_maker.public_data_collector.management.removers import FestivalInfoRemover


class Command(BaseCommand):
    help = 'Remove expired data'

    def __init__(self):
        super(Command, self).__init__()

        self.removers = [
            FestivalInfoRemover(),
        ]

    def handle(self, *args, **options):
        for remover in self.removers:
            remover.run()

        return 'removing data process complete.'
