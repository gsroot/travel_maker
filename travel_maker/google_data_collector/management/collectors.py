from datetime import datetime
from urllib.parse import urlencode, urljoin

import requests

from config.settings.base import GOOGLE_API_KEY
from travel_maker.google_data_collector.models import GooglePlaceInfo, GoogleApiProgress, GooglePlaceReviewInfo
from travel_maker.public_data_collector.models import TravelInfo


class Collector:
    def run(self):
        print("{} running...".format(self.__class__.__name__))


class WebCollector(Collector):
    base_url = 'https://maps.googleapis.com/maps/api/place/'
    base_query_params = {
        'language': 'ko',
        'key': GOOGLE_API_KEY,
    }

    def update_url(self, query_params):
        self.query_params = self.base_query_params.copy()
        self.query_params.update(query_params)

        self.url = self.endpoint + '?' + urlencode(self.query_params)

    def response_to_dict(self, response):
        response.raise_for_status()
        res_dict = response.json()

        if res_dict['status'] in ['ZERO_RESULTS', 'NOT_FOUND']:
            return None
        elif res_dict['status'] != 'OK':
            msg = '  request failed!\n    url:{}\n    status:{}'.format(self.url, res_dict['status'])
            raise UserWarning(msg)

        return res_dict


class GooglePlaceInfoCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'textsearch/json'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = GoogleApiProgress.objects.get_or_create(collector_type=self.__class__.__name__)[0]
        self.progress.set_total_item_count(TravelInfo.objects.count())

    def request(self):
        progress = self.progress

        travel_infos = TravelInfo.objects.all() if progress.travel_info is None \
            else TravelInfo.objects.filter(id__gte=progress.travel_info.id)

        for travel_info in travel_infos:
            progress.travel_info = travel_info
            progress.save()

            query_params = {
                'query': travel_info.title,
                'location': '{},{}'.format(travel_info.mapy, travel_info.mapx),
                'radius': '10000',
            }
            self.update_url(query_params)
            response = requests.get(self.url)

            try:
                res_dict = self.response_to_dict(response)
            except UserWarning as e:
                print(e)
                return

            if res_dict:
                info_dict = res_dict['results'][0]
                GooglePlaceInfo.objects.create(place_id=info_dict['place_id'], travel_info=travel_info)

            progress.item_complete_count += 1
            progress.percent = int(progress.item_complete_count * 100 / GoogleApiProgress.TOTAL_ITEM_CNT)
            progress.save()

    def run(self):
        super().run()
        if self.progress.percent >= 100:
            print("  Nothing to do")
            return
        self.request()


class GooglePlaceReviewInfoCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'details/json'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = GoogleApiProgress.objects.get_or_create(collector_type=self.__class__.__name__)[0]
        self.progress.set_total_item_count(GooglePlaceInfo.objects.count())

    def request(self):
        progress = self.progress

        place_infos = GooglePlaceInfo.objects.all() if progress.place_info is None \
            else GooglePlaceInfo.objects.filter(id__gte=progress.place_info.id)

        for place_info in place_infos:
            progress.place_info = place_info
            progress.save()

            query_params = {
                'placeid': place_info.place_id
            }
            self.update_url(query_params)
            response = requests.get(self.url)

            try:
                res_dict = self.response_to_dict(response)
            except UserWarning as e:
                print(e)
                return

            if res_dict:
                if 'reviews' in res_dict['result']:
                    reviews = res_dict['result']['reviews']
                    GooglePlaceReviewInfo.objects.bulk_create([
                        GooglePlaceReviewInfo(
                            place_info=place_info,
                            author_name=review['author_name'],
                            profile_photo_url=review['profile_photo_url'] if 'profile_photo_url' in review else '',
                            rating=review['rating'], text=review['text'],
                            time=datetime.fromtimestamp(float(review['time']))
                        ) for review in reviews
                    ])

            progress.item_complete_count += 1
            progress.percent = int(progress.item_complete_count * 100 / GoogleApiProgress.TOTAL_ITEM_CNT)
            progress.save()

    def run(self):
        super().run()
        if self.progress.percent >= 100:
            print("  Nothing to do")
            return
        self.request()
