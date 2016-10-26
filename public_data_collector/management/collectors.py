import json
import logging
from datetime import datetime
from urllib.parse import urlencode, urlunsplit, urljoin
from urllib.parse import urlsplit

import requests

from public_data_collector.models import AreaCodeProgress, Area, Sigungu, SmallArea, CategoryCodeProgress, Category1, \
    Category2, Category3, ContentType, TravelInfo, TravelOverviewInfo, TravelOverviewInfoProgress

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class Collector:
    def run(self):
        logger.info("{} running...".format(self.__class__.__name__))


class ContentTypeCollector(Collector):
    content_type_dict = {
        12: '관광지',
        14: '문화시설',
        15: '행사/공연/축제',
        25: '여행코스',
        28: '레포츠',
        32: '숙박',
        38: '쇼핑',
        39: '음식점'
    }

    def run(self):
        super().run()
        if ContentType.objects.count() != len(self.content_type_dict):
            ContentType.objects.all().delete()
            ContentType.objects.bulk_create([ContentType(id, name) for id, name in self.content_type_dict.items()])
        else:
            logger.info("  Nothing to do")


class WebCollector(Collector):
    base_url = 'http://api.visitkorea.or.kr/openapi/service/rest/KorService/'
    base_query_params = {
        'pageNo': 1,
        'MobileOS': 'ETC',
        'MobileApp': 'travel_maker',
        '_type': 'json',
    }
    service_keys = []
    service_key = ''

    def update_url(self, query_params):
        self.query_params = self.base_query_params.copy()
        self.query_params.update(query_params)

        split_result = urlsplit(self.endpoint)
        split_result = split_result._replace(query=urlencode(self.query_params))
        self.url = urlunsplit(split_result) + '&ServiceKey={}'.format(self.service_key)

    @classmethod
    def change_service_key(cls, idx):
        cls.service_key = cls.service_keys[idx % len(cls.service_keys)]


class AreacodeWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'areaCode'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = AreaCodeProgress.objects.get_or_create()[0]

    def _request(self, district_class, query_params, parent_dist):
        self.update_url(query_params)
        response = requests.get(self.url)
        response.raise_for_status()
        res_dict = response.json()

        if int(res_dict['response']['header']['resultCode']) != 0:
            msg = '  request failed!\n    url:{}\n    code:{}\n    msg:{}'.format(
                self.url, res_dict['response']['header']['resultCode'], res_dict['response']['header']['resultMsg']
            )
            raise UserWarning(msg)

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
            try:
                districts = self._request(district_class, query_params)
            except UserWarning as e:
                logger.warning(e)
                return
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

                try:
                    result = self._request(district_class, query_params, pd)
                except UserWarning as e:
                    logger.warning(e)
                    return

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
        super().run()

        progress = self.progress

        if progress.percent >= 100:
            logger.info("  Nothing to do")
            return

        areas = self.request_to_area() if progress.level <= AreaCodeProgress.AR else Area.objects.filter(
            id__gte=progress.area_id)
        sigungus = self.request_to_sigungu(areas) if progress.level <= AreaCodeProgress.SG else Sigungu.objects.filter(
            id__gte=progress.sigungu_id)
        self.request_to_smallarea(sigungus)


class CategorycodeWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'categoryCode'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = CategoryCodeProgress.objects.get_or_create()[0]

    def _request(self, category_class, query_params, parent_cat=None):
        self.update_url(query_params)
        response = requests.get(self.url)
        response.raise_for_status()
        res_dict = response.json()
        if res_dict['response']['body']['totalCount'] == 0:
            return []

        if int(res_dict['response']['header']['resultCode']) != 0:
            msg = '  request failed!\n    url:{}\n    code:{}\n    msg:{}'.format(
                self.url, res_dict['response']['header']['resultCode'], res_dict['response']['header']['resultMsg']
            )
            raise UserWarning(msg)

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
            try:
                categories = self._request(category_class, query_params)
            except UserWarning as e:
                logger.warning(e)
                return
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

                try:
                    result = self._request(category_class, query_params, pc)
                except UserWarning as e:
                    logger.warning(e)
                    return

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
        super().run()

        progress = self.progress

        if progress.percent >= 100:
            logger.info("  Nothing to do")
            return

        cat1s = self.request_to_cat1() if progress.level <= CategoryCodeProgress.C1 else Category1.objects.filter(
            id__gte=progress.cat1_id)
        cat2s = self.request_to_cat2(cat1s) if progress.level <= CategoryCodeProgress.C2 else Category2.objects.filter(
            id__gte=progress.cat2_id)
        self.request_to_cat3(cat2s)


class TravelInfoWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'areaBasedList'
        self.endpoint = urljoin(self.base_url, self.operation)

    def request(self):
        query_params = {
            'numOfRows': 100000,
        }
        self.update_url(query_params)
        response = requests.get(self.url)
        response.raise_for_status()
        res_dict = response.json()

        try:
            if int(res_dict['response']['header']['resultCode']) != 0:
                raise UserWarning
        except UserWarning:
            logger.warning(
                '  request failed!\n    url:{}\n    code:{}\n    msg:{}'.format(
                    self.url,
                    res_dict['response']['header']['resultCode'],
                    res_dict['response']['header']['resultMsg']
                )
            )
            return

        raw_travel_info_dicts = res_dict['response']['body']['items']['item']

        key_to_column_swithcer = {
            'contentid': 'id',
            'addr1': 'addr1',
            'addr2': 'addr2',
            'areacode': 'area_code',
            'sigungucode': 'sigungu_code',
            'contenttypeid': 'contenttype_id',
            'cat1': 'cat1_code',
            'cat2': 'cat2_code',
            'cat3': 'cat3_code',
            'title': 'title',
            'firstimage': 'image',
            'firstimage2': 'thumbnail',
            'mapx': 'mapx',
            'mapy': 'mapy',
            'mlevel': 'mlevel',
            'booktour': 'is_booktour',
            'tel': 'tel',
            'readcount': 'readcount',
            'createdtime': 'created',
            'modifiedtime': 'modified',
        }

        info_dicts = []
        for raw_info in raw_travel_info_dicts:
            info_dicts.append(
                {key_to_column_swithcer[key]: val for key, val in raw_info.items() if key in key_to_column_swithcer}
            )

        infos = []
        for info in info_dicts:
            if 'mlevel' in info and type(info['mlevel']) is not int:
                del info['mlevel']
            if 'readcount' in info and type(info['readcount']) is not int:
                del info['readcount']
            if 'area_code' in info and 'sigungu_code' in info:
                try:
                    info.update({
                        'sigungu': Sigungu.objects.get(area__code=info['area_code'], code=info['sigungu_code'])
                    })
                except Sigungu.DoesNotExist:
                    pass
            if 'cat3_code' in info:
                try:
                    info.update({
                        'cat3': Category3.objects.get(code=info['cat3_code'])
                    })
                except Category3.DoesNotExist:
                    pass
            if 'created' in info:
                try:
                    info.update({
                        'created': datetime.strptime(str(info['created']), '%Y%m%d%H%M%S')
                    })
                except ValueError:
                    pass
            if 'modified' in info:
                try:
                    info.update({
                        'modified': datetime.strptime(str(info['modified']), '%Y%m%d%H%M%S')
                    })
                except ValueError:
                    pass
            infos.append(TravelInfo(**info))

        TravelInfo.objects.bulk_create(infos)

    def run(self):
        super().run()
        if TravelInfo.objects.count() > 0:
            logger.info("  Nothing to do")
            return
        self.request()


class TravelOverviewInfoWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'detailCommon'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = TravelOverviewInfoProgress.objects.get_or_create()[0]

    def request(self):
        progress = self.progress

        infos = TravelInfo.objects.all() if progress.travel_info is None \
            else TravelInfo.objects.filter(id__gte=progress.travel_info.id)

        for info in infos:
            progress.travel_info = info
            progress.save()

            query_params = {
                'contentId': info.id,
                'defaultYN': 'Y',
                'overviewYN': 'Y',
            }
            self.update_url(query_params)
            response = requests.get(self.url)
            response.raise_for_status()
            res_dict = response.json()

            try:
                if int(res_dict['response']['header']['resultCode']) != 0:
                    raise UserWarning
            except UserWarning:
                logger.warning(
                    '  request failed!\n    url:{}\n    code:{}\n    msg:{}'.format(
                        self.url,
                        res_dict['response']['header']['resultCode'],
                        res_dict['response']['header']['resultMsg']
                    )
                )
                break

            info_dict = res_dict['response']['body']['items']['item']

            info = {
                'travel_info': info
            }
            if 'telname' in info_dict:
                info.update({
                    'telname': info_dict['telname'],
                })
            if 'homepage' in info_dict:
                info.update({
                    'homepage': info_dict['homepage'],
                })
            if 'overview' in info_dict:
                info.update({
                    'overview': info_dict['overview'],
                })
            TravelOverviewInfo.objects.create(**info)

            progress.info_complete_count += 1
            progress.percent = int(progress.info_complete_count * 100 / TravelOverviewInfoProgress.TOTAL_INFO_CNT)
            progress.save()

    def run(self):
        super().run()
        if self.progress.percent >= 100:
            logger.info("  Nothing to do")
            return
        self.request()


class PublicDataCollector:
    def __init__(self):
        super().__init__()

        with open('/etc/secrets/travel_maker/service_key.txt') as f:
            WebCollector.service_keys = json.loads(f.read().strip())
        WebCollector.service_key = WebCollector.service_keys[0]

        self.collectors = [
            ContentTypeCollector(),
            AreacodeWebCollector(),
            CategorycodeWebCollector(),
            TravelInfoWebCollector(),
            TravelOverviewInfoWebCollector()
        ]

    def run(self):
        for idx, key in enumerate(WebCollector.service_keys):
            for collector in self.collectors:
                collector.run()
            WebCollector.change_service_key(idx + 1)
