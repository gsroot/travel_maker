import json
from datetime import datetime
from json import JSONDecodeError
from urllib.parse import urlparse, parse_qs, urlunparse

import requests
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django.db import DataError
from django.db import IntegrityError

from config.settings.base import NAVER_API_CLIENT_ID, NAVER_API_CLIENT_SECRET
from travel_maker.blog_data_collector.forms import BlogDataForm
from travel_maker.blog_data_collector.models import BlogDataProgress
from travel_maker.public_data_collector.models import TravelInfo


class Collector:
    def run(self):
        print("{} running...".format(self.__class__.__name__))


class WebCollector(Collector):
    base_url = 'https://openapi.naver.com/v1/search/blog'
    url = base_url
    base_query_params = {
        'display': 50,
    }
    client_id = NAVER_API_CLIENT_ID
    client_secret = NAVER_API_CLIENT_SECRET

    def __init__(self):
        self.query_params = self.base_query_params.copy()

    def response_to_dict(self, response):
        response.raise_for_status()
        res_dict = json.loads(response.text)

        return res_dict


class BlogDataCollector(WebCollector):
    def __init__(self):
        super().__init__()
        self.progress = BlogDataProgress.objects.get_or_create(collector_type=self.__class__.__name__)[0]

    def get_travel_infos(self):
        datetime_before = datetime.today().date() - relativedelta(days=5)
        travel_infos = TravelInfo.objects.filter(blogdata__isnull=True,
                                                 tm_updated__gte=datetime_before).distinct().order_by('modified')

        return travel_infos

    def init_progress(self, progress, target_info_count):
        progress.target_info_count = target_info_count
        progress.info_complete_count = 0
        if progress.target_info_count == 0:
            progress.percent = 100
        else:
            progress.percent = 0
        progress.save()

    def set_travel_info_to_progress(self, progress, travel_info):
        progress.travel_info = travel_info
        progress.save()

    def update_progress(self, progress):
        progress.info_complete_count += 1
        progress.percent = int(progress.info_complete_count * 100 / progress.target_info_count)
        progress.save()

    def parse_blogs(self, blogs, travel_info):
        for blog in blogs:
            blog['travel_info'] = travel_info.id
            if blog['postdate']:
                blog['postdate'] = datetime.strptime(blog['postdate'], '%Y%m%d').date()
            blog['text'] = ''
            tags = []
            parse_result = urlparse(blog['link'])

            if parse_result.netloc == 'blog.naver.com':
                blog_id = parse_result.path[1:]
                log_no = parse_qs(parse_result.query)['logNo'][0]
                variables = json.dumps([{
                    "blogId": blog_id,
                    "logNo": log_no
                }])

                link = list(parse_result)
                link[4] = ''
                link[2] += '/' + log_no
                blog['link'] = urlunparse(link)

                link[1] = 'm.' + link[1]
                response = requests.get(urlunparse(link))
                soup = BeautifulSoup(response.text, 'html.parser')
                content_div = soup.find('div', class_='_postView')
                if not content_div:
                    continue
                blog['text'] = content_div.find('div', id='viewTypeSelector').get_text().strip()

                response = requests.get(
                    'http://section.blog.naver.com/TagSearchAsync.nhn?variables=' + variables
                )
                tags = response.json()[0]['tags']
                tags = [str(t) for t in tags]

            elif parse_result.netloc == 'blog.daum.net':
                link = list(parse_result)
                link[1] = 'm.' + link[1]
                response = requests.get(urlunparse(link))
                soup = BeautifulSoup(response.text, 'html.parser')
                article_div = soup.find('div', id='article')
                if not article_div:
                    continue
                [d.extract() for d in article_div.find_all('div')]
                blog['text'] = article_div.get_text().strip()

            elif parse_result.netloc.endswith('tistory.com'):
                response = requests.get(blog['link'])
                soup = BeautifulSoup(response.text, 'html.parser')
                content_div = soup.find('div', class_='tt_article_useless_p_margin')

                if not content_div:
                    content_div = soup.find('div', class_='article')
                if not content_div:
                    content_div = soup.find('div', class_='area_view')
                if not content_div:
                    content_div = soup.find('div', class_='desc')
                if not content_div:
                    content_div = soup.find('div', class_='content_data_main_data_desc')
                if not content_div:
                    continue

                [f.extract() for f in content_div.find_all('fieldset')]
                [d.extract() for d in content_div.find_all('div')]

                blog['text'] = content_div.get_text().strip()

                tags_div = soup.find('div', class_='tagTrail')
                if not tags_div:
                    tags_div = soup.find('dl', class_='list_tag')
                if not tags_div:
                    tags_div = soup.find('div', class_='tag')
                if not tags_div:
                    tags_div = soup.find('div', class_='content_data_bottom_tag')

                if tags_div:
                    tags = [tag.get_text() for tag in tags_div.find_all('a')]

            elif parse_result.netloc.endswith('egloos.com'):
                response = requests.get(blog['link'])
                soup = BeautifulSoup(response.text, 'html.parser')
                if not soup.find('div', class_='hentry'):
                    continue
                blog['text'] = soup.find('div', class_='hentry').get_text().strip()
                tags_div = soup.find('div', class_='post_taglist')

                if tags_div:
                    tags = [tag.get_text() for tag in tags_div.find_all('a')]

            blog['tags'] = ', '.join(tags)
            form = BlogDataForm(blog)
            if form.is_valid():
                form.save()

    def request(self):
        travel_infos = self.get_travel_infos()
        self.init_progress(self.progress, travel_infos.count())

        for travel_info in travel_infos:
            self.set_travel_info_to_progress(self.progress, travel_info)

            query_params = {
                'query': '{} ??????'.format(travel_info.title)
            }
            self.query_params.update(query_params)
            response = requests.get(self.url, headers={
                "X-Naver-Client-Id": self.client_id, "X-Naver-Client-Secret": self.client_secret
            }, params=self.query_params)

            try:
                res_dict = self.response_to_dict(response)
                if res_dict['total'] > 0:
                    blogs = res_dict['items']
                    self.parse_blogs(blogs, travel_info)
            except (JSONDecodeError, UnicodeEncodeError, IntegrityError, NotImplementedError, DataError) as e:
                print(e)
            finally:
                self.update_progress(self.progress)

    def run(self):
        super().run()
        self.request()
