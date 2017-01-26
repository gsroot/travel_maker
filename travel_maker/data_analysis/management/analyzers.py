from pprint import pprint
from statistics import mean

import nltk
import pickle
from konlpy.tag import Twitter

from travel_maker.blog_data_collector.models import BlogData
from travel_maker.data_analysis.models import DataAnalysisProgress
from travel_maker.public_data_collector.models import TravelInfo


class Analizer:
    def run(self):
        print("{} running...".format(self.__class__.__name__))


class BlogDataAnalizer(Analizer):
    train_rating_path = 'travel_maker/data_analysis/ratings_train.txt'
    test_rating_path = 'travel_maker/data_analysis/ratings_test.txt'
    selected_words_path = 'travel_maker/data_analysis/selected_words.pickle'
    words_and_ox_set = None

    def __init__(self):
        super().__init__()
        self.progress = DataAnalysisProgress.objects.get_or_create(collector_type=self.__class__.__name__)[0]
        self.pos_tagger = Twitter()

    def get_rating_filepath(self, target):
        filepath_dict = {
            'train': self.train_rating_path,
            'test': self.test_rating_path
        }

        return filepath_dict[target]

    def read_data(self, filepath):
        with open(filepath, 'r') as f:
            data = [line.split('\t') for line in f.read().splitlines()]
            data = data[1:]  # header 제외
        return data

    def tokenize(self, sentence):
        return ['/'.join(res) for res in self.pos_tagger.pos(sentence, norm=True, stem=True)]

    def text_features(self, words):
        selected_words = self.load_selected_words()
        return {'include({})'.format(sel_word): True for sel_word in selected_words if sel_word in words}

    def save_classifier(self, classifier):
        with open('travel_maker/data_analysis/classifier.pickle', 'wb') as f:
            pickle.dump(classifier, f, -1)

    def load_classifier(self):
        with open('travel_maker/data_analysis/classifier.pickle', 'rb') as f:
            classifier = pickle.load(f)

        return classifier

    def save_selected_words(self, selected_words):
        filepath = self.selected_words_path
        with open(filepath, 'wb') as f:
            pickle.dump(selected_words, f, -1)

    def load_selected_words(self):
        filepath = self.selected_words_path
        try:
            with open(filepath, 'rb') as f:
                selected_words = pickle.load(f)
        except IOError:
            words_and_ox_set = self.get_words_and_ox_set('train')
            text = nltk.Text([t for feature in words_and_ox_set for t in feature[0]], name='NMSC')
            selected_words = [f[0] for f in text.vocab().most_common(2000)]
            self.save_selected_words(selected_words)

        return selected_words

    def get_words_and_ox_set(self, target):
        if not self.words_and_ox_set:
            filepath = self.get_rating_filepath(target)
            self.words_and_ox_set = [(self.tokenize(row[1]), row[2]) for row in self.read_data(filepath)]

        return self.words_and_ox_set

    def get_featureset(self, target):
        words_and_ox_set = self.get_words_and_ox_set(target)

        words_and_ox_set = words_and_ox_set[:10000]
        featureset = [
            (self.text_features(words_and_ox[0]), words_and_ox[1])
            for words_and_ox in words_and_ox_set
            ]

        return featureset

    def get_trainset(self):
        return self.get_featureset('train')

    def get_testset(self):
        return self.get_featureset('test')

    def get_train_classifier(self):
        train_set = self.get_trainset()
        classifier = nltk.NaiveBayesClassifier.train(train_set)
        test_set = self.get_testset()
        print('트레이닝된 classfier의 정확도는 {}% 입니다'.format(100 * nltk.classify.accuracy(classifier, test_set)))
        classifier.show_most_informative_features(1000)

        self.save_classifier(classifier)

        return classifier

    def get_travel_infos(self):
        travel_infos = TravelInfo.objects.filter(score__isnull=True, blogdata__isnull=False).distinct().order_by('id')

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

    def get_score(self, travel_info):
        blog_count = travel_info.blogdata_set.all().count()
        blog_count = 30 if blog_count >= 30 else blog_count
        blog_score = travel_info.blog_score * (0.66 + 0.44 * blog_count / 30) if travel_info.blog_score else 30
        google_review_count = travel_info.googleplaceinfo.googleplacereviewinfo_set.all().count() \
            if hasattr(travel_info, 'googleplaceinfo') else 0
        rating_count = google_review_count + travel_info.travelreview_set.all().count()
        rating_count = 5 if rating_count >= 5 else rating_count
        rating_score = travel_info.rating * 20 * (1.2 + 0.8 * rating_count / 5) if travel_info.rating else 60
        score = int(round(blog_score + rating_score, 2))
        return score

    def score_travel_info(self):
        try:
            classifier = self.load_classifier()
        except IOError:
            classifier = self.get_train_classifier()

        travel_infos = self.get_travel_infos()
        self.init_progress(self.progress, travel_infos.count())

        for travel_info in travel_infos:
            self.set_travel_info_to_progress(self.progress, travel_info)

            if not travel_info.blog_score:
                blogs = BlogData.objects.filter(travel_info=travel_info)[:30]
                points = []
                for blog in blogs:
                    words = self.tokenize(blog.text)
                    blog.point = 1 if classifier.classify(self.text_features(words)) == '1' else 0
                    blog.save()
                    points.append(blog.point)
                travel_info.blog_score = round(mean(points), 2) * 100 if points else 0

            travel_info.score = self.get_score(travel_info)
            print('{}: 블로그 {}점 총 {}점'.format(travel_info.title, travel_info.blog_score, travel_info.score))
            travel_info.save()

            self.update_progress(self.progress)

    def run(self):
        super().run()
        self.score_travel_info()
