from datetime import datetime
from urllib.parse import urlencode, urljoin

import requests
from dateutil.relativedelta import relativedelta

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
            msg = '  request failed!\n    url:{}\n    status:{}\n    error_message:{}'.format(
                self.url, res_dict['status'], res_dict['error_message'])
            raise UserWarning(msg)

        return res_dict


class GoogleInfoCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.progress = GoogleApiProgress.objects.get_or_create(collector_type=self.__class__.__name__)[0]

    def get_target_infos(self):
        pass

    def init_progress(self, progress, target_info_count):
        progress.target_info_count = target_info_count
        progress.info_complete_count = 0
        if progress.target_info_count == 0:
            progress.percent = 100
        else:
            progress.percent = 0
        progress.save()

    def set_target_info_to_progress(self, progress, target_info):
        if target_info.__class__ == TravelInfo:
            progress.travel_info = target_info
        elif target_info.__class__ == GooglePlaceInfo:
            progress.place_info = target_info
        progress.save()

    def update_progress(self, progress):
        progress.info_complete_count += 1
        progress.percent = int(progress.info_complete_count * 100 / progress.target_info_count)
        progress.save()

    def get_query_params(self, travel_info):
        pass

    def run(self):
        super().run()
        if self.progress.last_progress_date.date() == datetime.today().date() and self.progress.percent >= 100:
            print("  Nothing to do")
            return
        self.request()


class GooglePlaceInfoCollector(GoogleInfoCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'textsearch/json'
        self.endpoint = urljoin(self.base_url, self.operation)

    def get_target_infos(self):
        datetime_before = datetime.today().date() - relativedelta(days=5)
        travel_infos = TravelInfo.objects.filter(tm_created__gte=datetime_before, googleplaceinfo__isnull=True) \
            .order_by('modified')
        return travel_infos

    def get_query_params(self, travel_info):
        query_params = {
            'query': travel_info.title,
            'location': '{},{}'.format(travel_info.mapy, travel_info.mapx),
            'radius': '10000',
        }
        return query_params

    def request(self):
        travel_infos = self.get_target_infos()
        self.init_progress(self.progress, travel_infos.count())

        for travel_info in travel_infos:
            self.set_target_info_to_progress(self.progress, travel_info)

            query_params = self.get_query_params(travel_info)
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

            self.update_progress(self.progress)


class GooglePlaceReviewInfoCollector(GoogleInfoCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'details/json'
        self.endpoint = urljoin(self.base_url, self.operation)

    def get_target_infos(self):
        place_infos = GooglePlaceInfo.objects.filter(googleplacereviewinfo__isnull=True)
        return place_infos

    def get_query_params(self, place_info):
        query_params = {
            'placeid': place_info.place_id
        }
        return query_params

    def request(self):
        place_infos = self.get_target_infos()
        self.init_progress(self.progress, place_infos.count())

        for place_info in place_infos:
            self.set_target_info_to_progress(self.progress, place_info)

            query_params = self.get_query_params(place_info)
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
                    GooglePlaceReviewInfo.objects.bulk_create([GooglePlaceReviewInfo(
                        place_info=place_info,
                        author_name=review['author_name'],
                        profile_photo_url=review[
                            'profile_photo_url'] if 'profile_photo_url' in review else '',
                        rating=review['rating'], text=review['text'],
                        time=datetime.fromtimestamp(float(review['time']))
                    ) for review in reviews])

            self.update_progress(self.progress)
