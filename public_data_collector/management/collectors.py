import json
from datetime import datetime
from urllib.parse import urlencode, urlunsplit, urljoin
from urllib.parse import urlsplit

import requests

from public_data_collector.models import AreaCodeProgress, Area, Sigungu, SmallArea, CategoryCodeProgress, Category1, \
    Category2, Category3, ContentType, TravelInfo, TravelOverviewInfo, AdditionalInfoProgress, TravelIntroInfo, \
    TourspotIntroInfo, CulturalFacilityIntroInfo, FestivalIntroInfo, TourCourseIntroInfo, \
    LeportsIntroInfo, LodgingIntroInfo, ShoppingIntroInfo, RestaurantIntroInfo, TravelDetailInfo, \
    DefaultTravelDetailInfo, TourCourseDetailInfo, LodgingDetailInfo, TravelImageInfo


class Collector:
    def run(self):
        print("{} running...".format(self.__class__.__name__))


class ContentTypeConstant:
    TOURSPOT = ContentType(12, '관광')
    CULTURAL_FACILITY = ContentType(14, '문화시설')
    FESTIVAL = ContentType(15, '행사/공연/축제')
    TOUR_COURSE = ContentType(25, '여행코스')
    LEPORTS = ContentType(28, '레포츠')
    LODGING = ContentType(32, '숙박')
    SHOPPING = ContentType(38, '쇼핑')
    RESTAURANT = ContentType(39, '음식점')


class ContentTypeCollector(Collector):
    content_types = [
        ContentTypeConstant.TOURSPOT,
        ContentTypeConstant.CULTURAL_FACILITY,
        ContentTypeConstant.FESTIVAL,
        ContentTypeConstant.TOUR_COURSE,
        ContentTypeConstant.LEPORTS,
        ContentTypeConstant.LODGING,
        ContentTypeConstant.SHOPPING,
        ContentTypeConstant.RESTAURANT
    ]

    def run(self):
        super().run()

        if ContentType.objects.count() == len(self.content_types):
            print("  Nothing to do")
            return

        ContentType.objects.all().delete()
        ContentType.objects.bulk_create(self.content_types)


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

    def response_to_dict(self, response):
        response.raise_for_status()
        res_dict = response.json()

        if int(res_dict['response']['header']['resultCode']) != 0:
            msg = '  request failed!\n    url:{}\n    code:{}\n    msg:{}'.format(
                self.url, res_dict['response']['header']['resultCode'], res_dict['response']['header']['resultMsg']
            )
            raise UserWarning(msg)

        return res_dict


class DepthItemWebCollector(WebCollector):
    def _request(self, target_class, query_params, parent):
        self.update_url(query_params)
        response = requests.get(self.url)
        res_dict = self.response_to_dict(response)

        if res_dict['response']['body']['totalCount'] == 0:
            return []

        item_dicts = res_dict['response']['body']['items']['item']
        if type(item_dicts) is not list:
            item_dicts = [item_dicts]
        for d in item_dicts:
            del d['rnum']

        if target_class is Category1:
            items = [target_class(**d) for d in item_dicts]
        elif target_class is Category2:
            items = [target_class(**d, area=parent) for d in item_dicts]
        else:
            items = [target_class(**d, sigungu=parent) for d in item_dicts]

        target_class.objects.bulk_create(items)

        return target_class.objects.all()

    def request(self, item_class, parent_items=None):
        query_params = {
            'numOfRows': 1000,
        }

        progress = self.progress
        depth_switcher = {
            Area: AreaCodeProgress.AR,
            Sigungu: AreaCodeProgress.SG,
            SmallArea: AreaCodeProgress.SM,
            Category1: CategoryCodeProgress.C1,
            Category2: CategoryCodeProgress.C2,
            Category3: CategoryCodeProgress.C3,
        }
        progress.depth = depth_switcher[item_class]
        progress.save()

        items = []
        if item_class is self.dep1_class:
            try:
                items = self._request(item_class, query_params)
            except UserWarning as e:
                print(e)
                return
        else:
            for parent_item in parent_items:
                if item_class is self.dep2_class:
                    query_params.update({
                        self.query_param_dep1: parent_item.code,
                    })
                    self.progress_dep1 = parent_item
                else:
                    grand_parent = parent_item.area if self.__class__ is AreacodeWebCollector else parent_item.cat1
                    query_params.update({
                        self.query_param_dep1: grand_parent.code,
                        self.query_param_dep2: parent_item.code,
                    })
                    self.progress_dep2 = parent_item
                    if self.progress_dep1.code != grand_parent.code:
                        self.progress_dep1 = grand_parent

                parent_item.save()
                progress.save()

                try:
                    result = self._request(item_class, query_params, parent_item)
                except UserWarning as e:
                    print(e)
                    return

                if item_class is self.dep1_class:
                    items += result
                else:
                    grand_parent = parent_item.area if self.__class__ is AreacodeWebCollector else parent_item.cat1
                    if self.progress_dep1.code != grand_parent.code:
                        self.progress_dep1_complete_count += 1
                        progress.percent = int(self.progress_dep1_complete_count * 100 / self.total_dep1_count)
                        progress.save()

        return items

    def request_to_depth1(self):
        return self.request(self.dep1_class)

    def request_to_depth2(self, dep1_items):
        return self.request(self.dep2_class, dep1_items)

    def request_to_depth3(self, dep2_items):
        return self.request(self.dep3_class, dep2_items)

    def run(self):
        super().run()

        if self.progress.percent >= 100:
            print("  Nothing to do")
            return

        dep1_items = self.request_to_depth1() if self.progress.depth <= self.progress_dep1 \
            else self.dep1_class.objects.filter(id__gte=self.progress_dep1_item.id)
        dep2_items = self.request_to_depth2(dep1_items) if self.progress.depth <= self.progress_dep2 \
            else self.dep2_class.objects.filter(id__gte=self.progress_dep2_item.id)
        self.request_to_depth3(dep2_items)


class AreacodeWebCollector(DepthItemWebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'areaCode'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = AreaCodeProgress.objects.get_or_create()[0]

        self.dep1_class = Area
        self.dep2_class = Sigungu
        self.dep3_class = SmallArea
        self.progress_dep1 = AreaCodeProgress.AR
        self.progress_dep2 = AreaCodeProgress.SG
        self.progress_dep1_item = self.progress.area
        self.progress_dep2_item = self.progress.sigungu
        self.query_param_dep1 = 'areaCode'
        self.query_param_dep2 = 'sigunguCode'
        self.progress_dep1_complete_count = self.progress.area_complete_count
        self.total_dep1_count = AreaCodeProgress.TOTAL_AREA_CNT


class CategorycodeWebCollector(DepthItemWebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'areaCode'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = CategoryCodeProgress.objects.get_or_create()[0]

        self.dep1_class = Category1
        self.dep2_class = Category2
        self.dep3_class = Category3
        self.progress_dep1 = CategoryCodeProgress.C1
        self.progress_dep2 = CategoryCodeProgress.C2
        self.progress_dep1_item = self.progress.cat1
        self.progress_dep2_item = self.progress.cat2
        self.query_param_dep1 = 'cat1'
        self.query_param_dep2 = 'cat2'
        self.progress_dep1_complete_count = self.progress.cat1_complete_count
        self.total_dep1_count = CategoryCodeProgress.TOTAL_CATEGORY_CNT


class TravelInfoWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'areaBasedList'
        self.endpoint = urljoin(self.base_url, self.operation)

    def _update_info_dict(self, info_dict):
        if 'mlevel' in info_dict and type(info_dict['mlevel']) is not int:
            del info_dict['mlevel']
        if 'readcount' in info_dict and type(info_dict['readcount']) is not int:
            del info_dict['readcount']
        if 'area_code' in info_dict and 'sigungu_code' in info_dict:
            try:
                info_dict.update({
                    'sigungu': Sigungu.objects.get(area__code=info_dict['area_code'], code=info_dict['sigungu_code'])
                })
            except Sigungu.DoesNotExist:
                pass
        if 'cat3_code' in info_dict:
            try:
                info_dict.update({
                    'cat3': Category3.objects.get(code=info_dict['cat3_code'])
                })
            except Category3.DoesNotExist:
                pass
        if 'created' in info_dict:
            try:
                info_dict.update({
                    'created': datetime.strptime(str(info_dict['created']), '%Y%m%d%H%M%S')
                })
            except ValueError:
                pass
        if 'modified' in info_dict:
            try:
                info_dict.update({
                    'modified': datetime.strptime(str(info_dict['modified']), '%Y%m%d%H%M%S')
                })
            except ValueError:
                pass

    def request(self):
        query_params = {
            'numOfRows': 100000,
        }
        self.update_url(query_params)
        response = requests.get(self.url)
        try:
            res_dict = self.response_to_dict(response)
        except UserWarning as e:
            print(e)
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
        for info_dict in info_dicts:
            self._update_info_dict(info_dict)
            infos.append(TravelInfo(**info_dict))

        TravelInfo.objects.bulk_create(infos)

    def run(self):
        super().run()
        if TravelInfo.objects.all().exists():
            print("  Nothing to do")
            return
        self.request()


class TravelOverviewInfoWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'detailCommon'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = AdditionalInfoProgress.objects.get_or_create(info_type=TravelOverviewInfo.__name__)[0]

    def _update_info_dict(self, info_dict):
        del info_dict['contentid']
        del info_dict['contenttypeid']

        new_info_dict = {key: value for key, value in info_dict.items() if key in ['telname', 'homepage', 'overview']}
        info_dict.clear()
        info_dict.update(new_info_dict)

    def request(self):
        progress = self.progress

        travel_infos = TravelInfo.objects.all() if progress.travel_info is None \
            else TravelInfo.objects.filter(id__gte=progress.travel_info.id)

        for travel_info in travel_infos:
            progress.travel_info = travel_info
            progress.save()

            query_params = {
                'contentId': travel_info.id,
                'defaultYN': 'Y',
                'overviewYN': 'Y',
            }
            self.update_url(query_params)
            response = requests.get(self.url)
            try:
                res_dict = self.response_to_dict(response)
            except UserWarning as e:
                print(e)
                return

            if res_dict['response']['body']['totalCount'] != 0:
                info_dict = res_dict['response']['body']['items']['item']
                self._update_info_dict(info_dict)
                info_dict.update({
                    'travel_info': travel_info
                })

                TravelOverviewInfo.objects.create(**info_dict)

            progress.info_complete_count += 1
            progress.percent = int(progress.info_complete_count * 100 / AdditionalInfoProgress.TOTAL_TRAVEL_INFO_CNT)
            progress.save()

    def run(self):
        super().run()
        if self.progress.percent >= 100:
            print("  Nothing to do")
            return
        self.request()


class TravelIntroInfoWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'detailIntro'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = AdditionalInfoProgress.objects.get_or_create(info_type=TravelIntroInfo.__name__)[0]

    def _update_info_dict(self, info_dict):
        if 'contentid' in info_dict:
            del info_dict['contentid']
        if 'contenttypeid' in info_dict:
            del info_dict['contenttypeid']
        if 'culturecenter' in info_dict:
            del info_dict['culturecenter']

        new_info_dict = dict()

        for key, value in info_dict.items():
            key = key.replace('usetimefestival', 'usefee') \
                .replace('culture', '') \
                .replace('festival', '') \
                .replace('tourcourse', '') \
                .replace('leports', '') \
                .replace('lodging', '') \
                .replace('shopping', '')
            if self.info_class is RestaurantIntroInfo:
                key = key.replace('food', '')
            if key in ['eventstartdate', 'eventenddate']:
                try:
                    value = datetime.strptime(str(value), '%Y%m%d')
                except ValueError:
                    pass

            new_info_dict.update({key: value})

        info_dict.clear()
        info_dict.update(new_info_dict)

    def request(self):
        progress = self.progress

        travel_infos = TravelInfo.objects.all() if progress.travel_info is None \
            else TravelInfo.objects.filter(id__gte=progress.travel_info.id)

        for travel_info in travel_infos:
            progress.travel_info = travel_info
            progress.save()

            query_params = {
                'contentId': travel_info.id,
                'contentTypeId': travel_info.contenttype.id,
            }
            self.update_url(query_params)
            response = requests.get(self.url)
            try:
                res_dict = self.response_to_dict(response)
            except UserWarning as e:
                print(e)
                return

            if res_dict['response']['body']['totalCount'] != 0:
                info_class_swithcer = {
                    ContentTypeConstant.TOURSPOT.id: TourspotIntroInfo,
                    ContentTypeConstant.CULTURAL_FACILITY.id: CulturalFacilityIntroInfo,
                    ContentTypeConstant.FESTIVAL.id: FestivalIntroInfo,
                    ContentTypeConstant.TOUR_COURSE.id: TourCourseIntroInfo,
                    ContentTypeConstant.LEPORTS.id: LeportsIntroInfo,
                    ContentTypeConstant.LODGING.id: LodgingIntroInfo,
                    ContentTypeConstant.SHOPPING.id: ShoppingIntroInfo,
                    ContentTypeConstant.RESTAURANT.id: RestaurantIntroInfo,
                }
                self.info_class = info_class_swithcer[travel_info.contenttype.id]

                info_dict = res_dict['response']['body']['items']['item']
                self._update_info_dict(info_dict)
                info_dict.update({
                    'travel_info': travel_info
                })

                self.info_class.objects.create(**info_dict)

            progress.info_complete_count += 1
            progress.percent = int(progress.info_complete_count * 100 / AdditionalInfoProgress.TOTAL_TRAVEL_INFO_CNT)
            progress.save()

    def run(self):
        super().run()
        if self.progress.percent >= 100:
            print("  Nothing to do")
            return
        self.request()


class TravelDetailInfoWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'detailInfo'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = AdditionalInfoProgress.objects.get_or_create(info_type=TravelDetailInfo.__name__)[0]

    def _update_info_dict(self, info_dict):
        if 'contentid' in info_dict:
            del info_dict['contentid']
        if 'contenttypeid' in info_dict:
            del info_dict['contenttypeid']

        if self.info_class is DefaultTravelDetailInfo and 'fldgubun' in info_dict:
            del info_dict['fldgubun']
        elif self.info_class is TourCourseDetailInfo and 'subcontentid' in info_dict:
            info_dict['sub_travel_info'] = info_dict.pop('subcontentid')
        elif self.info_class is LodgingDetailInfo and 'roomcode' in info_dict:
            del info_dict['roomcode']

    def request(self):
        progress = self.progress

        travel_infos = TravelInfo.objects.all() if progress.travel_info is None \
            else TravelInfo.objects.filter(id__gte=progress.travel_info.id)

        for travel_info in travel_infos:
            progress.travel_info = travel_info
            progress.save()

            query_params = {
                'contentId': travel_info.id,
                'contentTypeId': travel_info.contenttype.id,
            }
            self.update_url(query_params)
            response = requests.get(self.url)
            try:
                res_dict = self.response_to_dict(response)
            except UserWarning as e:
                print(e)
                return

            if res_dict['response']['body']['totalCount'] != 0:
                info_class_swithcer = {
                    ContentTypeConstant.TOURSPOT.id: DefaultTravelDetailInfo,
                    ContentTypeConstant.CULTURAL_FACILITY.id: DefaultTravelDetailInfo,
                    ContentTypeConstant.FESTIVAL.id: DefaultTravelDetailInfo,
                    ContentTypeConstant.TOUR_COURSE.id: TourCourseDetailInfo,
                    ContentTypeConstant.LEPORTS.id: DefaultTravelDetailInfo,
                    ContentTypeConstant.LODGING.id: LodgingDetailInfo,
                    ContentTypeConstant.SHOPPING.id: DefaultTravelDetailInfo,
                    ContentTypeConstant.RESTAURANT.id: DefaultTravelDetailInfo,
                }
                self.info_class = info_class_swithcer[travel_info.contenttype.id]

                info_dicts = res_dict['response']['body']['items']['item']
                if type(info_dicts) is not list:
                    info_dicts = [info_dicts]

                for info_dict in info_dicts:
                    self._update_info_dict(info_dict)
                    info_dict.update({
                        'travel_info': travel_info
                    })

                    self.info_class.objects.create(**info_dict)

            progress.info_complete_count += 1
            progress.percent = int(progress.info_complete_count * 100 / AdditionalInfoProgress.TOTAL_TRAVEL_INFO_CNT)
            progress.save()

    def run(self):
        super().run()
        if self.progress.percent >= 100:
            print("  Nothing to do")
            return
        self.request()


class TravelImageInfoWebCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.operation = 'detailImage'
        self.endpoint = urljoin(self.base_url, self.operation)
        self.progress = AdditionalInfoProgress.objects.get_or_create(info_type=TravelImageInfo.__name__)[0]

    def _update_info_dict(self, info_dict):
        if 'contentid' in info_dict:
            del info_dict['contentid']
        if 'imgname' in info_dict:
            del info_dict['imgname']

    def request(self):
        progress = self.progress

        travel_infos = TravelInfo.objects.all() if progress.travel_info is None \
            else TravelInfo.objects.filter(id__gte=progress.travel_info.id)

        for travel_info in travel_infos:
            progress.travel_info = travel_info
            progress.save()

            query_params = {
                'contentId': travel_info.id,
            }

            req_cnt_per_travel_info = 1 if travel_info.contenttype is not ContentTypeConstant.RESTAURANT else 2

            for i in range(req_cnt_per_travel_info):
                if i == 1:
                    query_params.update({
                        'imageYN': 'N'
                    })
                self.update_url(query_params)
                response = requests.get(self.url)
                try:
                    res_dict = self.response_to_dict(response)
                except UserWarning as e:
                    print(e)
                    if travel_info.contenttype is ContentTypeConstant.RESTAURANT and i == 0:
                        TravelImageInfo.objects.get(travel_info=travel_info).delete()
                    return

                if res_dict['response']['body']['totalCount'] != 0:
                    info_dicts = res_dict['response']['body']['items']['item']
                    if type(info_dicts) is not list:
                        info_dicts = [info_dicts]

                    for info_dict in info_dicts:
                        self._update_info_dict(info_dict)
                        info_dict.update({
                            'travel_info': travel_info
                        })

                        TravelImageInfo.objects.create(**info_dict)

            progress.info_complete_count += 1
            progress.percent = int(progress.info_complete_count * 100 / AdditionalInfoProgress.TOTAL_TRAVEL_INFO_CNT)
            progress.save()

    def run(self):
        super().run()
        if self.progress.percent >= 100:
            print("  Nothing to do")
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
            TravelOverviewInfoWebCollector(),
            TravelIntroInfoWebCollector(),
            TravelDetailInfoWebCollector(),
            TravelImageInfoWebCollector(),
        ]

    def run(self):
        for idx, key in enumerate(WebCollector.service_keys):
            for collector in self.collectors:
                collector.run()
            WebCollector.change_service_key(idx + 1)
