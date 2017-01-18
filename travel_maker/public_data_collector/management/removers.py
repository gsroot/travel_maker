from datetime import datetime

from dateutil.relativedelta import relativedelta

from travel_maker.public_data_collector.models import TravelInfo


class Remover:
    def run(self):
        print("{} running...".format(self.__class__.__name__))


class FestivalInfoRemover(Remover):
    def get_expired_infos(self):
        before = datetime.today().date() - relativedelta(months=1)
        expired_infos = TravelInfo.objects.filter(festivalintroinfo__eventenddate__lt=before)
        return expired_infos

    def remove_expired(self):
        expired_infos = self.get_expired_infos()
        deleted, deleted_count = expired_infos.delete()
        print('=== deleted count ===\n{}'.format(deleted_count))

    def run(self):
        super().run()
        self.remove_expired()
