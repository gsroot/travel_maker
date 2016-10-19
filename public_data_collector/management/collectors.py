from urllib.parse import urlencode, urlunsplit, urljoin
from urllib.parse import urlsplit

import requests

from public_data_collector.models import AreaCodeProgress, Area, Sigungu, SmallArea, CategoryCodeProgress, Category1, \
    Category2, Category3


class Collector:
    def __init__(self):
        super(Collector, self).__init__()
        self.base_url = 'http://api.visitkorea.or.kr/openapi/service/rest/KorService/'
        with open('/etc/secrets/travel_maker/service_key.txt') as f:
            self.service_key = f.read().strip()
        self.base_query_params = {
            'pageNo': 1,
            'MobileOS': 'ETC',
            'MobileApp': 'travel_maker',
        }

    def update_setting(self, query_params):
        self.query_params = self.base_query_params.copy()
        self.query_params.update(query_params)

        split_result = urlsplit(self.endpoint)
        split_result = split_result._replace(query=urlencode(self.query_params))
        self.url = urlunsplit(split_result) + '&ServiceKey={}'.format(self.service_key)


class AreaCodeCollector(Collector):
    def __init__(self):
        super(AreaCodeCollector, self).__init__()
        self.operation = 'areaCode'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = AreaCodeProgress.objects.get_or_create()[0]

    def _request(self, district_class, query_params, parent_dist):
        self.update_setting(query_params)
        response = requests.get(self.url)
        response.raise_for_status()
        res_dict = response.json()
        if res_dict['response']['body']['totalCount'] == 0:
            return []

        district_dicts = res_dict['response']['body']['items']['item']
        if type(district_dicts) is not list:
            district_dicts = [district_dicts]
        for d in district_dicts:
            del d['rnum']

        if district_class == Category1:
            districts = [district_class(**d) for d in district_dicts]
        elif district_class == Category2:
            districts = [district_class(**d, area=parent_dist) for d in district_dicts]
        else:
            districts = [district_class(**d, sigungu=parent_dist) for d in district_dicts]

        district_class.objects.bulk_create(districts)

        return district_class.objects.all()

    def request(self, district_class, parent_districts=None):
        query_params = {
            'numOfRows': 1000,
            '_type': 'json',
        }

        level_switcher = {
            Area: AreaCodeProgress.AR,
            Sigungu: AreaCodeProgress.SG,
            SmallArea: AreaCodeProgress.SM
        }
        progress = self.progress
        progress.level = level_switcher[district_class]
        progress.save()

        districts = []
        if district_class == Area:
            districts = self._request(district_class, query_params)
        else:
            for pd in parent_districts:
                if district_class == Sigungu:
                    query_params.update({
                        'areaCode': pd.code,
                    })
                    progress.area = pd
                else:
                    query_params.update({
                        'areaCode': pd.area.code,
                        'sigunguCode': pd.code,
                    })
                    progress.sigungu = pd
                    if progress.area.code != pd.area.code:
                        progress.area = pd.area

                pd.save()
                progress.save()

                result = self._request(district_class, query_params, pd)

                if district_class == Sigungu:
                    districts += result
                elif progress.area.code != pd.area.code:
                    progress.area_complete_count += 1
                    progress.percent = int(progress.area_complete_count * 100 / AreaCodeProgress.TOTAL_AREA_CNT)
                    progress.save()

        return districts

    def request_to_area(self):
        return self.request(Area)

    def request_to_sigungu(self, areas):
        return self.request(Sigungu, areas)

    def request_to_smallarea(self, sigungus):
        return self.request(SmallArea, sigungus)

    def run(self):
        progress = self.progress

        if progress.percent >= 100:
            return

        areas = self.request_to_area() if progress.level <= AreaCodeProgress.AR else Area.objects.filter(
            id__gte=progress.area_id)
        sigungus = self.request_to_sigungu(areas) if progress.level <= AreaCodeProgress.SG else Sigungu.objects.filter(
            id__gte=progress.sigungu_id)
        self.request_to_smallarea(sigungus)


class CategoryCodeCollector(Collector):
    def __init__(self):
        super(CategoryCodeCollector, self).__init__()
        self.operation = 'categoryCode'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = CategoryCodeProgress.objects.get_or_create()[0]

    def _request(self, category_class, query_params, parent_cat=None):
        self.update_setting(query_params)
        response = requests.get(self.url)
        response.raise_for_status()
        res_dict = response.json()
        if res_dict['response']['body']['totalCount'] == 0:
            return []

        category_dicts = res_dict['response']['body']['items']['item']
        if type(category_dicts) is not list:
            category_dicts = [category_dicts]
        for c in category_dicts:
            del c['rnum']

        if category_class == Category1:
            categories = [category_class(**c) for c in category_dicts]
        elif category_class == Category2:
            categories = [category_class(**c, cat1=parent_cat) for c in category_dicts]
        else:
            categories = [category_class(**c, cat2=parent_cat) for c in category_dicts]

        category_class.objects.bulk_create(categories)

        return category_class.objects.all()

    def request(self, category_class, parent_cats=None):
        query_params = {
            'numOfRows': 1000,
            '_type': 'json',
        }

        level_switcher = {
            Category1: CategoryCodeProgress.C1,
            Category2: CategoryCodeProgress.C2,
            Category3: CategoryCodeProgress.C3
        }
        progress = self.progress
        progress.level = level_switcher[category_class]
        progress.save()

        categories = []
        if category_class == Category1:
            categories = self._request(category_class, query_params)
        else:
            for pc in parent_cats:
                if category_class == Category2:
                    query_params.update({
                        'cat1': pc.code,
                    })
                    progress.cat1 = pc
                else:
                    query_params.update({
                        'cat1': pc.cat1.code,
                        'cat2': pc.code,
                    })
                    progress.cat2 = pc
                    if progress.cat1.code != pc.cat1.code:
                        progress.cat1 = pc.cat1
                progress.save()

                result = self._request(category_class, query_params, pc)

                if category_class == Category2:
                    categories += result
                elif progress.cat1.code != pc.cat1.code:
                    progress.cat1_complete_count += 1
                    progress.percent = int(progress.cat1_complete_count * 100 / AreaCodeProgress.TOTAL_AREA_CNT)
                    progress.save()

        return categories

    def request_to_cat1(self):
        return self.request(Category1)

    def request_to_cat2(self, cat1s):
        return self.request(Category2, cat1s)

    def request_to_cat3(self, cat2s):
        self.request(Category3, cat2s)

    def run(self):
        progress = self.progress

        if progress.percent >= 100:
            return

        cat1s = self.request_to_cat1() if progress.level <= CategoryCodeProgress.C1 else Category1.objects.filter(
            id__gte=progress.cat1_id)
        cat2s = self.request_to_cat2(cat1s) if progress.level <= CategoryCodeProgress.C2 else Category2.objects.filter(
            id__gte=progress.cat2_id)
        self.request_to_cat3(cat2s)


class PublicDataCollector:
    def __init__(self):
        super(PublicDataCollector, self).__init__()
        self.areacode_collector = AreaCodeCollector()
        self.categorycode_collector = CategoryCodeCollector()

    def run(self):
        self.areacode_collector.run()
        self.categorycode_collector.run()
