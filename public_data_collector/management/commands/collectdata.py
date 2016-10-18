import requests
from django.core.management.base import BaseCommand
from django.utils.http import urlencode

from public_data_collector.models import Area, Sigungu, SmallArea, Progress


class Collector:
    def __init__(self):
        super(Collector, self).__init__()
        self.base_url = 'http://api.visitkorea.or.kr/openapi/service/rest/KorService'
        self.endpoint = self.base_url
        with open('/etc/secrets/travel_maker/service_key.txt') as f:
            self.service_key = f.read().strip()
        self.base_query_params = {
            'pageNo': 1,
            'MobileOS': 'ETC',
            'MobileApp': 'culterdata_proto',
        }
        self.progress = Progress.objects.get_or_create()[0]

    def update_setting(self, query_params):
        self.query_params = self.base_query_params.copy()
        self.query_params.update(query_params)
        self.endpoint = self.base_url \
                        + '/areaCode?ServiceKey={}&{}'.format(self.service_key, urlencode(self.query_params))

    def send_request(self):
        return requests.get(self.endpoint)

    def request_to_area(self):
        self.progress.level = Progress.AR
        self.progress.save()

        self.update_setting({
            'numOfRows': 1000,
            '_type': 'json',
        })
        response = self.send_request()
        response.raise_for_status()
        res_dict = response.json()
        area_dicts = res_dict['response']['body']['items']['item']
        areas = [Area(code=area['code'], name=area['name']) for area in area_dicts]
        Area.objects.bulk_create(areas)

        return areas

    def request_to_sigungu(self, areas):
        progress = self.progress
        progress.level = Progress.SG
        progress.save()

        all_sigungus = []
        for area in areas:
            area.save()
            progress.area = area
            progress.save()

            self.update_setting({
                'numOfRows': 1000,
                '_type': 'json',
                'areaCode': area.code,
            })
            response = self.send_request()
            response.raise_for_status()
            res_dict = response.json()
            sigungu_dicts = res_dict['response']['body']['items']['item']
            if type(sigungu_dicts) is not list:
                sigungu_dicts = [sigungu_dicts]
            sigungus = [Sigungu(area=area, code=sigungu['code'], name=sigungu['name']) for sigungu in
                        sigungu_dicts]
            Sigungu.objects.bulk_create(sigungus)
            all_sigungus += sigungus

        return all_sigungus

    def request_to_smallarea(self, sigungus):
        progress = self.progress
        progress.level = Progress.SM
        progress.save()

        for sigungu in sigungus:
            if progress.area.code != sigungu.area.code:
                progress.area = sigungu.area
            sigungu.save()
            progress.sigungu = sigungu
            progress.save()

            self.update_setting({
                'numOfRows': 1000,
                '_type': 'json',
                'areaCode': sigungu.area.code,
                'sigunguCode': sigungu.code
            })
            response = self.send_request()
            response.raise_for_status()
            res_dict = response.json()
            if res_dict['response']['body']['totalCount'] == 0:
                continue
            smallarea_dicts = res_dict['response']['body']['items']['item']
            smallareas = [SmallArea(sigungu=sigungu, code=smallarea['code'], name=smallarea['name']) for
                          smallarea in smallarea_dicts]
            SmallArea.objects.bulk_create(smallareas)

            if progress.area.code != sigungu.area.code:
                progress.fully_completed_area_count += 1
                progress.percent = int(progress.fully_completed_area_count * 100 / Progress.TOTAL_AREA_CNT)

    def run(self):
        progress = self.progress
        areas = self.request_to_area() if progress.level <= Progress.AR else Area.objects.filter(
            id__gte=progress.area_id)
        sigungus = self.request_to_sigungu(areas) if progress.level <= Progress.SG else Sigungu.objects.filter(
            id__gte=progress.sigungu_id)
        self.request_to_smallarea(sigungus)


class Command(Collector, BaseCommand):
    help = 'Collect public data'

    def __init__(self):
        super(Command, self).__init__()

    def handle(self, *args, **options):
        self.run()
        return 'collecting data process complete.'
